"""MILP baseline model (PuLP). Simplified three-echelon aggregate."""
from __future__ import annotations

import pulp
import pandas as pd


def solve(
    demand: pd.DataFrame,
    suppliers: pd.DataFrame,
    scenario: dict | None = None,
    horizon: int = 30,
    transport_mult: float = 1.0,
) -> dict:
    prob = pulp.LpProblem("supply_chain", pulp.LpMinimize)

    supply = pulp.LpVariable.dicts("supply", [(s, t) for s in suppliers.supplier_id for t in range(1, horizon + 1)], lowBound=0)
    backorder = pulp.LpVariable.dicts("backorder", range(1, horizon + 1), lowBound=0)

    total_demand = demand.groupby("day")["demand"].sum()
    cap = suppliers.set_index("supplier_id")["capacity"]

    # Landed unit cost = purchase (₹4) + transport (₹1 × transport_mult).
    unit_cost = 4 + transport_mult
    prob += pulp.lpSum(supply[(s, t)] * unit_cost for s in suppliers.supplier_id for t in range(1, horizon + 1)) + pulp.lpSum(backorder[t] * 50 for t in range(1, horizon + 1))

    for t in range(1, horizon + 1):
        prob += pulp.lpSum(supply[(s, t)] for s in suppliers.supplier_id) + backorder[t] >= total_demand.get(t, 0)
        for s in suppliers.supplier_id:
            c = 0 if scenario and s == scenario.get("supplier") and scenario["start"] <= t < scenario["start"] + scenario["duration"] else cap[s]
            prob += supply[(s, t)] <= c

    try:
        prob.solve(pulp.HiGHS(msg=0))
    except Exception:
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return {
        "status": pulp.LpStatus[prob.status],
        "cost": pulp.value(prob.objective),
        "backorders": sum(backorder[t].value() or 0 for t in range(1, horizon + 1)),
    }
