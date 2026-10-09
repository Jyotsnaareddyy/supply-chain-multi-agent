"""Generate a reproducible three-echelon network dataset."""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent
SEED = 42

SUPPLIERS = ["S1", "S2"]
WAREHOUSES = ["WH1", "WH2", "WH3"]
CUSTOMERS = ["C1", "C2", "C3", "C4", "C5", "C6"]
PRODUCTS = ["P1", "P2"]
HORIZON = 30


def generate() -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(SEED)

    products = pd.DataFrame(
        {
            "product_id": PRODUCTS,
            "unit_cost": rng.integers(50, 200, len(PRODUCTS)),
            "holding_cost": rng.uniform(0.5, 2.0, len(PRODUCTS)).round(2),
        }
    )

    suppliers = pd.DataFrame(
        {
            "supplier_id": SUPPLIERS,
            "capacity": [700, 450],
            "lead_time": [3, 4],
            "risk_score": [0.35, 0.21],
        }
    )

    warehouses = pd.DataFrame(
        {
            "warehouse_id": WAREHOUSES,
            "capacity": [2000, 2000, 1500],
            "safety_stock": [200, 200, 150],
        }
    )

    customers = pd.DataFrame(
        {
            "customer_id": CUSTOMERS,
            "warehouse_id": ["WH1", "WH1", "WH2", "WH2", "WH3", "WH3"],
            "demand": rng.integers(80, 160, len(CUSTOMERS)),
            "priority": ["high", "high", "medium", "medium", "low", "low"],
        }
    )

    demand_rows = []
    for _, c in customers.iterrows():
        for day in range(1, HORIZON + 1):
            demand_rows.append(
                {
                    "customer_id": c.customer_id,
                    "day": day,
                    "demand": max(0, int(rng.normal(c.demand, c.demand * 0.1))),
                }
            )
    demand = pd.DataFrame(demand_rows)

    inventory = pd.DataFrame(
        [
            {"location": w, "product": p, "opening_inventory": int(rng.integers(150, 350))}
            for w in ["DC"] + WAREHOUSES
            for p in PRODUCTS
        ]
    )

    transport = pd.DataFrame(
        [
            {"origin": "S1", "destination": "DC", "mode": "road", "cost": 5, "lead_time": 3},
            {"origin": "S2", "destination": "DC", "mode": "road", "cost": 6, "lead_time": 4},
            {"origin": "S2", "destination": "DC", "mode": "air", "cost": 18, "lead_time": 1},
            *[
                {"origin": "DC", "destination": w, "mode": "road", "cost": 3, "lead_time": 1}
                for w in WAREHOUSES
            ],
        ]
        + [
            {"origin": w, "destination": w2, "mode": "road", "cost": 4, "lead_time": 1}
            for i, w in enumerate(WAREHOUSES)
            for w2 in WAREHOUSES
            if w != w2
        ]
    )

    scenarios = pd.DataFrame(
        [
            {
                "scenario_id": "S1_DISRUPTION_01",
                "supplier": "S1",
                "disruption_start": 10,
                "duration": 7,
            }
        ]
    )

    constraints = pd.DataFrame(
        [
            {
                "service_level": 0.95,
                "max_expedite": 400,
                "max_capacity_s2": 600,
            }
        ]
    )

    return {
        "products": products,
        "suppliers": suppliers,
        "warehouses": warehouses,
        "customers": customers,
        "demand": demand,
        "inventory": inventory,
        "transport": transport,
        "scenarios": scenarios,
        "constraints": constraints,
    }


def write_all() -> None:
    for name, df in generate().items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
        print(f"wrote {name}.csv ({len(df)} rows)")


if __name__ == "__main__":
    write_all()
