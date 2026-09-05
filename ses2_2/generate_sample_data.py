"""Generate a synthetic pharma supply-chain shipment dataset for the risk analyzer demo.

Usage:
    python generate_sample_data.py [--rows 250] [--seed 7] [--excursion-rate 0.12] [--out pharma_shipments.xlsx]
"""
import argparse
import datetime as dt

import numpy as np
import pandas as pd

PRODUCTS = [
    "Insulin Glargine", "Amoxicillin", "Fentanyl Patch", "Oxycodone HCl",
    "COVID-19 mRNA Vaccine", "Trastuzumab", "Atorvastatin", "Adalimumab",
    "Morphine Sulfate", "Warfarin Sodium", "Human Growth Hormone", "Ibuprofen",
]
CONTROLLED = {"Fentanyl Patch", "Oxycodone HCl", "Morphine Sulfate", "Human Growth Hormone"}
CITIES = [
    "Mumbai, IN", "Basel, CH", "Indianapolis, US", "Singapore, SG", "Cork, IE",
    "Shanghai, CN", "Hyderabad, IN", "Frankfurt, DE", "New Jersey, US", "Sao Paulo, BR",
]
CARRIERS = ["AeroCold Logistics", "PharmaSwift", "MedEx Global", "ColdChain Direct", "RapidRx Freight"]


def generate(rows: int, seed: int, excursion_rate: float, delay_heavy_rate: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    products = rng.choice(PRODUCTS, size=rows)
    controlled = np.isin(products, list(CONTROLLED))
    origin = rng.choice(CITIES, size=rows)
    destination = np.array([rng.choice([c for c in CITIES if c != o]) for o in origin])
    carrier = rng.choice(CARRIERS, size=rows)

    ship_start = dt.date(2026, 1, 1)
    ship_offsets = rng.integers(0, 240, size=rows)
    ship_dates = [ship_start + dt.timedelta(days=int(d)) for d in ship_offsets]

    # cold-chain band: most products ship 2-8C, a few ambient (15-25C)
    is_cold_chain = rng.random(rows) < 0.7
    required_temp_min = np.where(is_cold_chain, 2.0, 15.0)
    required_temp_max = np.where(is_cold_chain, 8.0, 25.0)

    excursion = rng.random(rows) < excursion_rate
    recorded_temp_min = required_temp_min.copy()
    recorded_temp_max = required_temp_max.copy()
    excursion_delta = rng.uniform(1.5, 6.0, size=rows)
    recorded_temp_max = np.where(excursion, required_temp_max + excursion_delta, required_temp_max - rng.uniform(0.1, 1.0, size=rows))
    recorded_temp_min = np.where(excursion & (rng.random(rows) < 0.3), required_temp_min - excursion_delta, required_temp_min + rng.uniform(0.1, 1.0, size=rows))

    heavy_delay = rng.random(rows) < delay_heavy_rate
    delay_days = np.where(
        heavy_delay,
        rng.integers(6, 21, size=rows),
        rng.integers(-1, 4, size=rows),
    )

    value_tier = rng.random(rows)
    product_value_usd = np.where(
        value_tier < 0.1,
        rng.uniform(60_000, 250_000, size=rows),
        rng.uniform(500, 45_000, size=rows),
    ).round(2)

    delivered = rng.random(rows) < 0.9
    delivery_dates = [
        sd + dt.timedelta(days=int(max(dd, 0)) + int(rng.integers(1, 5))) if delivered[i] else None
        for i, (sd, dd) in enumerate(zip(ship_dates, delay_days))
    ]

    df = pd.DataFrame({
        "shipment_id": [f"SHIP-{i+1:05d}" for i in range(rows)],
        "product_name": products,
        "controlled_substance": controlled,
        "origin": origin,
        "destination": destination,
        "carrier": carrier,
        "ship_date": ship_dates,
        "delivery_date": delivery_dates,
        "required_temp_min_c": required_temp_min.round(1),
        "required_temp_max_c": required_temp_max.round(1),
        "recorded_temp_min_c": recorded_temp_min.round(1),
        "recorded_temp_max_c": recorded_temp_max.round(1),
        "delay_days": delay_days,
        "product_value_usd": product_value_usd,
    })
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=250)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--excursion-rate", type=float, default=0.12)
    parser.add_argument("--delay-heavy-rate", type=float, default=0.15)
    parser.add_argument("--out", type=str, default="pharma_shipments.xlsx")
    args = parser.parse_args()

    df = generate(args.rows, args.seed, args.excursion_rate, args.delay_heavy_rate)
    df.to_excel(args.out, index=False, sheet_name="shipments")
    print(f"Wrote {len(df)} rows to {args.out}")


if __name__ == "__main__":
    main()
