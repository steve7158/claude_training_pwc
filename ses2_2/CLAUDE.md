# Pharma Shipment Risk Analyzer

A single-page Streamlit app. Upload a shipment Excel file (or use the bundled
sample) and it shows: total shipments, high-risk count, temperature-excursion
count, the top 5 highest-risk shipments, a risk-distribution chart, and a
short heuristic recommendation section.

## Run it

```
source .venv/bin/activate  # or: pip install -r requirements.txt
streamlit run app.py
```

Regenerate the sample dataset with `python generate_sample_data.py` (flags:
`--rows`, `--seed`, `--excursion-rate`, `--delay-heavy-rate`, `--out`).

## Data schema

One sheet, one row per shipment. Required columns (see `generate_sample_data.py`
for exact generation logic):

`shipment_id, product_name, controlled_substance (bool), origin, destination,
carrier, ship_date, delivery_date, required_temp_min_c, required_temp_max_c,
recorded_temp_min_c, recorded_temp_max_c, delay_days, product_value_usd`

## Risk-scoring rules — the single source of truth

Defined in `score_shipments()` in [app.py](app.py). If asked to change risk
criteria, edit that function (and this table) together — never hardcode the
formula anywhere else:

| condition | points |
|---|---|
| temperature excursion (recorded outside required band) | +40 |
| delay_days > 2 (cold-chain, required_temp_max_c <= 10) or > 5 (ambient) | +20 |
| controlled_substance is true | +15 |
| product_value_usd > 50,000 | +15 |
| delay_days > 10 (severe delay, any product) | +10 |

Score is clipped to 0–100. `risk_level`: High >= 60, Medium 30–59, Low < 30.

The "Recommendations" section (`render_recommendations()`) is **deterministic
and template-based** — it is explicitly not an LLM call, so the app has zero
external dependencies. Keep it that way unless the user asks for a real LLM
integration; if they do, gate it behind an API-key check with a fallback to
the heuristic version.

## Conventions

- Keep this as a single-file app (`app.py`) unless it grows past ~300 lines.
- No comments except where a rule/threshold is non-obvious (e.g. the
  cold-chain delay threshold above) — the risk table in this file is the
  place for rule documentation, not inline comments.
- Chart colors use the status palette (good/warning/critical), not generic
  categorical colors — risk levels are a status, not an identity.
- No test suite exists; use the `streamlit-tester` subagent to verify the app
  still boots and renders after changes to `app.py`.
- Use the `streamlit-frontend` subagent for UI/UX work (layout, widgets,
  chart styling) — it knows to leave `score_shipments()` and the risk table
  alone and to follow the status-palette rule above.
