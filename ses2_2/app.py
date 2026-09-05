"""Pharma Shipment Risk Analyzer — Streamlit app.

Risk-scoring rules (see CLAUDE.md for the authoritative spec):
  +40 temperature excursion, +20 delay (>2d cold-chain / >5d ambient),
  +15 controlled substance, +15 value > $50k, +10 delay > 10d.
  risk_level: High >=60, Medium 30-59, Low <30.
"""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

SAMPLE_PATH = "pharma_shipments.xlsx"

STATUS_COLORS = {"Low": "#0ca30c", "Medium": "#fab219", "High": "#d03b3b"}
RISK_ORDER = ["Low", "Medium", "High"]


def score_shipments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    is_cold_chain = df["required_temp_max_c"] <= 10
    delay_threshold = is_cold_chain.map({True: 2, False: 5})

    excursion = (df["recorded_temp_max_c"] > df["required_temp_max_c"]) | (
        df["recorded_temp_min_c"] < df["required_temp_min_c"]
    )
    df["temperature_excursion"] = excursion

    score = pd.Series(0, index=df.index)
    score += excursion.astype(int) * 40
    score += (df["delay_days"] > delay_threshold).astype(int) * 20
    score += df["controlled_substance"].astype(int) * 15
    score += (df["product_value_usd"] > 50_000).astype(int) * 15
    score += (df["delay_days"] > 10).astype(int) * 10

    df["risk_score"] = score.clip(upper=100)
    df["risk_level"] = pd.cut(
        df["risk_score"], bins=[-1, 29, 59, 100], labels=["Low", "Medium", "High"]
    )
    return df


def render_recommendations(df: pd.DataFrame) -> list[str]:
    notes = []
    total = len(df)

    excursion_rate = df["temperature_excursion"].mean()
    if excursion_rate > 0.08:
        worst_carrier = (
            df[df["temperature_excursion"]]["carrier"].value_counts().idxmax()
        )
        pct = df[df["carrier"] == worst_carrier]["temperature_excursion"].mean() * 100
        notes.append(
            f"Temperature excursions affect {excursion_rate:.0%} of shipments. "
            f"**{worst_carrier}** has the highest excursion rate ({pct:.0f}% of its shipments) — "
            "audit its cold-chain equipment and handoff procedures."
        )

    high_risk = df[df["risk_level"] == "High"]
    if len(high_risk):
        controlled_share = high_risk["controlled_substance"].mean()
        if controlled_share > 0.2:
            notes.append(
                f"{controlled_share:.0%} of high-risk shipments involve controlled substances — "
                "prioritize chain-of-custody review for these lanes."
            )

    delayed = df[df["delay_days"] > 10]
    if len(delayed) / total > 0.05:
        worst_route = (
            (delayed["origin"] + " -> " + delayed["destination"]).value_counts().idxmax()
        )
        notes.append(
            f"{len(delayed)} shipments ({len(delayed)/total:.0%}) were delayed more than 10 days. "
            f"The **{worst_route}** route shows up most often — consider an alternate carrier or route."
        )

    high_value_risk = df[(df["product_value_usd"] > 50_000) & (df["risk_level"] != "Low")]
    if len(high_value_risk):
        notes.append(
            f"{len(high_value_risk)} high-value shipments (>$50k) carry elevated risk — "
            "these represent the largest potential loss exposure and warrant insurance/escort review."
        )

    if not notes:
        notes.append("No major risk patterns detected in this dataset — shipments are broadly on-track.")

    return notes


def render_risk_chart(df: pd.DataFrame):
    counts = df["risk_level"].value_counts().reindex(RISK_ORDER, fill_value=0)

    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    bars = ax.bar(
        counts.index,
        counts.values,
        color=[STATUS_COLORS[level] for level in counts.index],
        width=0.5,
    )
    for bar, value in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(counts.values) * 0.02,
            str(value),
            ha="center",
            va="bottom",
            color="#0b0b0b",
            fontsize=10,
        )

    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors="#52514e")
    ax.set_yticks([])
    ax.set_ylabel("")
    ax.set_title("Risk distribution", color="#0b0b0b", fontsize=12, loc="left")

    st.pyplot(fig, use_container_width=False)


def main():
    st.set_page_config(page_title="Pharma Shipment Risk Analyzer", layout="wide")
    st.title("Pharma Shipment Risk Analyzer")

    uploaded = st.file_uploader("Upload a shipment Excel file", type=["xlsx"])
    use_sample = st.button("Use sample data")

    if uploaded is not None:
        raw = pd.read_excel(uploaded)
    elif use_sample or "df" not in st.session_state:
        raw = pd.read_excel(SAMPLE_PATH)
    else:
        raw = st.session_state["df"]
    st.session_state["df"] = raw

    df = score_shipments(raw)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total shipments", len(df))
    col2.metric("High-risk shipments", int((df["risk_level"] == "High").sum()))
    col3.metric("Temperature excursions", int(df["temperature_excursion"].sum()))

    st.subheader("Top 5 highest-risk shipments")
    top5 = df.sort_values("risk_score", ascending=False).head(5)
    st.dataframe(
        top5[[
            "shipment_id", "product_name", "carrier", "risk_score", "risk_level",
            "temperature_excursion", "delay_days", "product_value_usd",
        ]],
        hide_index=True,
        use_container_width=True,
    )

    left, right = st.columns([1, 1.5])
    with left:
        render_risk_chart(df)
    with right:
        st.subheader("Recommendations")
        for note in render_recommendations(df):
            st.markdown(f"- {note}")
        st.caption("Heuristic-generated from the loaded data — not an LLM call.")


if __name__ == "__main__":
    main()
