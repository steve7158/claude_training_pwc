---
name: refresh-sample-data
description: Regenerate the synthetic pharma_shipments.xlsx sample dataset with a different size or anomaly rate (temperature excursions, delays). Use when someone asks for fresh test data, a bigger dataset, or wants to stress-test the app with more/fewer high-risk shipments.
---

# Refresh sample data

The app ships with a generated dataset at `pharma_shipments.xlsx`, built by
`generate_sample_data.py`. Don't hand-edit the xlsx or invent a new generator —
reuse this script and just vary its flags:

```
python generate_sample_data.py \
  --rows 250 \
  --seed 7 \
  --excursion-rate 0.12 \
  --delay-heavy-rate 0.15 \
  --out pharma_shipments.xlsx
```

- `--rows`: total shipment count.
- `--excursion-rate`: fraction of rows with a temperature excursion built in
  (drives the "Temperature excursions" metric and chart).
- `--delay-heavy-rate`: fraction of rows with a severe delay (6-20 days).
- `--seed`: change for a different random draw at the same rates; keep fixed
  for reproducible demos.
- `--out`: write to a different filename to keep the original sample intact
  for comparison (e.g. `pharma_shipments_stress.xlsx`).

After regenerating, if the request was to change risk behavior (not just data
volume), remember the actual risk logic lives in `score_shipments()` in
`app.py` — this script only produces raw shipment rows, it never assigns
risk scores or levels itself.
