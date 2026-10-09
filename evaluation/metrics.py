"""Evaluation metrics: fill rate, backorders, TLC, inventory days, recovery time."""
from __future__ import annotations


def fill_rate(demand_total: float, backorders: float) -> float:
    return (demand_total - backorders) / demand_total if demand_total else 1.0


def inventory_days(avg_inventory: float, avg_daily_demand: float) -> float:
    return avg_inventory / avg_daily_demand if avg_daily_demand else float("inf")


def recovery_time(daily_service: list[float], target: float) -> int | None:
    for i in range(len(daily_service)):
        window = daily_service[i : i + 3]
        if len(window) == 3 and all(s >= target for s in window):
            return i + 1
    return None
