"""SIP Calculator — Streamlit app.

Computes the future value of a monthly Systematic Investment Plan (SIP),
with an optional annual step-up in the monthly contribution.
"""
import time

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from otel_setup import get_meter, get_tracer, init_telemetry

init_telemetry()
tracer = get_tracer(__name__)
meter = get_meter(__name__)

schedule_computations = meter.create_counter(
    "sip.schedule.computations", description="Number of SIP schedule computations"
)
schedule_duration_ms = meter.create_histogram(
    "sip.schedule.duration_ms",
    description="Duration of computing the SIP schedule",
    unit="ms",
)

COLORS = {"invested": "#3b6fd0", "returns": "#0ca36e"}


def compute_sip_schedule(
    monthly_investment: float,
    annual_rate_pct: float,
    years: int,
    step_up_pct: float = 0.0,
) -> pd.DataFrame:
    monthly_rate = annual_rate_pct / 100 / 12

    rows = []
    invested_total = 0.0
    value_total = 0.0
    current_monthly = monthly_investment

    for year in range(1, years + 1):
        for _ in range(12):
            value_total = (value_total + current_monthly) * (1 + monthly_rate)
            invested_total += current_monthly
        rows.append(
            {
                "year": year,
                "invested": invested_total,
                "value": value_total,
                "returns": value_total - invested_total,
            }
        )
        current_monthly *= 1 + step_up_pct / 100

    return pd.DataFrame(rows)


def render_growth_chart(schedule: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    ax.plot(
        schedule["year"], schedule["invested"],
        label="Invested amount", color=COLORS["invested"], linewidth=2,
    )
    ax.plot(
        schedule["year"], schedule["value"],
        label="Total value", color=COLORS["returns"], linewidth=2,
    )
    ax.fill_between(
        schedule["year"], schedule["invested"], schedule["value"],
        color=COLORS["returns"], alpha=0.12,
    )

    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["bottom", "left"]].set_color("#c3c2b7")
    ax.tick_params(colors="#52514e")
    ax.set_xlabel("Year", color="#52514e")
    ax.set_ylabel("Amount", color="#52514e")
    ax.set_title("Investment growth over time", color="#0b0b0b", fontsize=12, loc="left")
    ax.legend(frameon=False, loc="upper left")

    st.pyplot(fig, use_container_width=True)


def render_breakdown_chart(invested: float, returns: float):
    fig, ax = plt.subplots(figsize=(3.5, 4))
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    labels = ["Invested", "Returns"]
    values = [invested, returns]
    colors = [COLORS["invested"], COLORS["returns"]]

    bars = ax.bar(labels, values, color=colors, width=0.5)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.02,
            f"{value:,.0f}",
            ha="center", va="bottom", color="#0b0b0b", fontsize=10,
        )

    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors="#52514e")
    ax.set_yticks([])
    ax.set_title("Invested vs. returns", color="#0b0b0b", fontsize=12, loc="left")

    st.pyplot(fig, use_container_width=False)


def main():
    st.set_page_config(page_title="SIP Calculator", layout="wide")
    st.title("SIP Calculator")
    st.caption("Estimate the future value of a monthly Systematic Investment Plan.")

    with st.sidebar:
        st.header("Inputs")
        monthly_investment = st.number_input(
            "Monthly investment", min_value=500, max_value=1_000_000,
            value=5_000, step=500,
        )
        annual_rate_pct = st.slider(
            "Expected annual return (%)", min_value=1.0, max_value=30.0,
            value=12.0, step=0.5,
        )
        years = st.slider("Investment duration (years)", min_value=1, max_value=40, value=10)
        step_up_pct = st.slider(
            "Annual step-up in SIP (%)", min_value=0.0, max_value=50.0,
            value=0.0, step=1.0,
            help="Increase the monthly investment by this percentage each year.",
        )

    with tracer.start_as_current_span("compute_sip_schedule") as span:
        span.set_attribute("sip.monthly_investment", monthly_investment)
        span.set_attribute("sip.annual_rate_pct", annual_rate_pct)
        span.set_attribute("sip.years", years)
        span.set_attribute("sip.step_up_pct", step_up_pct)

        start = time.perf_counter()
        schedule = compute_sip_schedule(monthly_investment, annual_rate_pct, years, step_up_pct)
        schedule_duration_ms.record((time.perf_counter() - start) * 1000)
        schedule_computations.add(1)

    final = schedule.iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total invested", f"{final['invested']:,.0f}")
    col2.metric("Estimated returns", f"{final['returns']:,.0f}")
    col3.metric("Total value", f"{final['value']:,.0f}")

    left, right = st.columns([2, 1])
    with left:
        with tracer.start_as_current_span("render_growth_chart"):
            render_growth_chart(schedule)
    with right:
        with tracer.start_as_current_span("render_breakdown_chart"):
            render_breakdown_chart(final["invested"], final["returns"])

    st.subheader("Year-by-year breakdown")
    st.dataframe(
        schedule.style.format({"invested": "{:,.0f}", "value": "{:,.0f}", "returns": "{:,.0f}"}),
        hide_index=True,
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
