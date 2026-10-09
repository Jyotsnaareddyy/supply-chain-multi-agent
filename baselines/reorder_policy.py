"""Conventional reorder-rule baseline: ROP = demand_leadtime + safety_stock."""
from __future__ import annotations

import pandas as pd


def reorder_policy(demand: pd.DataFrame, warehouses: pd.DataFrame) -> dict:
    avg_daily = demand.groupby("customer_id")["demand"].mean().sum()
    lead_time = 4  # days
    results = {}
    for _, w in warehouses.iterrows():
        rop = avg_daily * lead_time + w["safety_stock"]
        results[w["warehouse_id"]] = {"rop": rop, "safety_stock": w["safety_stock"]}
    return {"policy": "reorder_rule", "avg_daily_demand": avg_daily, "warehouses": results}


def simulate(
    demand: pd.DataFrame,
    inventory: pd.DataFrame,
    scenario: dict | None = None,
    lead_time: int = 4,
    disruption_supply_cap: float = 450.0,
    normal_supply_cap: float = 3000.0,
) -> dict:
    """Aggregate DC-level simulation of a fixed ROP reorder policy.

    The policy does not adapt to disruptions: it keeps ordering on its
    standard cadence, so arrivals are capped at nominal S2 capacity
    during the disruption window.
    """
    daily = demand.groupby("day")["demand"].sum().sort_index()
    avg = daily.mean()
    std = daily.std() or 0.0
    safety = 1.65 * std * (lead_time ** 0.5)
    rop = avg * lead_time + safety

    dc_stock = inventory[inventory["location"] == "DC"]["opening_inventory"].sum()
    # Assume the policy is in steady state at horizon start.
    stock = float(max(dc_stock, rop))
    total_unmet = 0.0
    pipeline: dict[int, float] = {}  # arrival_day -> quantity

    placed_qty = 0.0
    for day in daily.index:
        arrivals = pipeline.pop(day, 0.0)
        disrupted = (
            scenario
            and scenario["start"] <= day < scenario["start"] + scenario["duration"]
        )
        cap = disruption_supply_cap if disrupted else normal_supply_cap
        arrivals = min(arrivals, cap)
        stock += arrivals

        d = daily[day]
        if stock >= d:
            stock -= d
        else:
            total_unmet += d - stock
            stock = 0

        inventory_position = stock + sum(pipeline.values())
        order_qty = max(0.0, rop - inventory_position)
        if order_qty > 0:
            pipeline[day + lead_time] = pipeline.get(day + lead_time, 0.0) + order_qty
            placed_qty += order_qty

    backorder_cost = total_unmet * 50
    purchase_cost = placed_qty * 5
    holding_cost = max(stock, 0) * 1.0
    return {
        "policy": "reorder_rule",
        "rop": rop,
        "ending_stock": stock,
        "backorders": total_unmet,
        "fill_rate": 1 - total_unmet / daily.sum() if daily.sum() else 1.0,
        "cost": backorder_cost + purchase_cost + holding_cost,
    }
