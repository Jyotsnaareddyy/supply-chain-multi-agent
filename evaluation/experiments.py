"""Run the scenario matrix across all three approaches."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCENARIOS = [
    {"name": "Baseline", "disruption": None, "demand_mult": 1.0, "transport_mult": 1.0},
    {"name": "S1-7D", "disruption": {"supplier": "S1", "start": 10, "duration": 7}, "demand_mult": 1.0, "transport_mult": 1.0},
    {"name": "S1-7D-D10", "disruption": {"supplier": "S1", "start": 10, "duration": 7}, "demand_mult": 1.1, "transport_mult": 1.0},
    {"name": "S1-7D-T20", "disruption": {"supplier": "S1", "start": 10, "duration": 7}, "demand_mult": 1.0, "transport_mult": 1.2},
    {"name": "S1-7D-D10-T20", "disruption": {"supplier": "S1", "start": 10, "duration": 7}, "demand_mult": 1.1, "transport_mult": 1.2},
]


def run() -> pd.DataFrame:
    demand = pd.read_csv(DATA / "demand.csv")
    suppliers = pd.read_csv(DATA / "suppliers.csv")
    warehouses = pd.read_csv(DATA / "warehouses.csv")

    from agents.demand_agent import DemandAgent
    from agents.inventory_agent import InventoryAgent
    from agents.logistics_agent import LogisticsAgent
    from agents.supplier_risk_agent import SupplierRiskAgent
    from baselines.reorder_policy import reorder_policy
    from coordinator.conflict_resolver import ConflictResolver
    from coordinator.coordinator import Coordinator
    from coordinator.validator import Validator
    from optimization.milp_model import solve

    customers = pd.read_csv(DATA / "customers.csv")
    inventory = pd.read_csv(DATA / "inventory.csv")
    scenarios_df = pd.read_csv(DATA / "scenarios.csv")
    constraints = pd.read_csv(DATA / "constraints.csv")
    transport = pd.read_csv(DATA / "transport.csv")

    rows = []
    for sc in SCENARIOS:
        scenario_rows, _, _ = evaluate_scenario(sc, demand, suppliers, warehouses, customers, inventory, scenarios_df, constraints, transport)
        rows.extend(scenario_rows)
    return pd.DataFrame(rows)


def evaluate_scenario(sc, demand, suppliers, warehouses, customers, inventory, scenarios_df, constraints, transport):
    """Run all three approaches for one scenario dict. Returns (rows, accepted, rejected)."""
    from agents.demand_agent import DemandAgent
    from agents.inventory_agent import InventoryAgent
    from agents.logistics_agent import LogisticsAgent
    from agents.supplier_risk_agent import SupplierRiskAgent
    from baselines.reorder_policy import simulate as reorder_sim
    from coordinator.conflict_resolver import ConflictResolver
    from coordinator.coordinator import Coordinator
    from coordinator.validator import Validator
    from optimization.milp_model import solve

    rows = []
    d = demand.copy()
    d["demand"] = (d["demand"] * sc["demand_mult"]).round().astype(int)
    total_demand = float(d["demand"].sum())

    def _fill_rate(backorders: float) -> float:
        return round(1 - backorders / total_demand, 4) if total_demand else 1.0

    start = time.perf_counter()
    transport_mult = sc.get("transport_mult", 1.0)
    milp = solve(d, suppliers, scenario=sc["disruption"], transport_mult=transport_mult)
    milp_runtime = time.perf_counter() - start
    rows.append({"scenario": sc["name"], "approach": "milp", "cost": milp["cost"],
                 "backorders": milp["backorders"], "fill_rate": _fill_rate(milp["backorders"]),
                 "runtime_s": round(milp_runtime, 3),
                 "recs_accepted": 0, "recs_rejected": 0})

    start = time.perf_counter()
    scenario_id = "S1_DISRUPTION_01" if sc["disruption"] else "BASELINE"
    recs = []
    if sc["disruption"]:
        recs = [DemandAgent(d, customers).run(scenario_id),
                InventoryAgent(inventory, warehouses).run(scenario_id),
                SupplierRiskAgent(suppliers, scenarios_df).run(scenario_id),
                LogisticsAgent(transport).run(scenario_id)]

    validator = Validator(suppliers, warehouses, constraints)
    outcome = Coordinator(validator, ConflictResolver(capacity=450)).coordinate(recs)
    accepted = outcome["accepted"]

    suppliers_ma = suppliers.copy()
    extra_cap = sum(r.recommendation.quantity or 0 for r in accepted
                    if r.recommendation.source in suppliers_ma.supplier_id.values
                    and r.recommendation.action in ("alternate_source", "expedite"))
    if extra_cap:
        target = "S2" if (not sc["disruption"] or sc["disruption"]["supplier"] == "S1") else "S1"
        suppliers_ma.loc[suppliers_ma["supplier_id"] == target, "capacity"] += extra_cap
    expedite_cost = sum(r.expected_cost for r in accepted if r.recommendation.action == "expedite")

    milp_ma = solve(d, suppliers_ma, scenario=sc["disruption"], transport_mult=transport_mult)
    ma_runtime = time.perf_counter() - start
    rows.append({"scenario": sc["name"], "approach": "multi_agent",
                 "cost": (milp_ma["cost"] or 0) + expedite_cost, "backorders": milp_ma["backorders"],
                 "fill_rate": _fill_rate(milp_ma["backorders"]),
                 "runtime_s": round(ma_runtime, 3), "recs_accepted": len(accepted),
                 "recs_rejected": len(outcome["rejected"])})

    start = time.perf_counter()
    rw = reorder_sim(d, inventory, scenario=sc["disruption"])
    rw_runtime = time.perf_counter() - start
    rows.append({"scenario": sc["name"], "approach": "reorder_rule", "cost": rw["cost"],
                 "backorders": rw["backorders"], "fill_rate": _fill_rate(rw["backorders"]),
                 "runtime_s": round(rw_runtime, 3),
                 "recs_accepted": 0, "recs_rejected": 0})

    return rows, accepted, outcome["rejected"]


if __name__ == "__main__":
    print(run().to_string(index=False))
