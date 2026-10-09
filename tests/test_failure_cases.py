"""Failure/governance cases: bad inputs, infeasibility, agent conflicts."""
import pandas as pd

from baselines.reorder_policy import simulate
from coordinator.conflict_resolver import ConflictResolver
from coordinator.coordinator import Coordinator
from coordinator.validator import Validator
from optimization.milp_model import solve
from schemas.recommendation import Recommendation, RecommendationPayload


def _rec(agent, action, source, destination, quantity):
    return Recommendation(scenario_id="S", agent=agent, timestamp="t",
                          recommendation=RecommendationPayload(action=action, source=source, destination=destination, quantity=quantity))


def test_empty_demand_reorder_sim_does_not_crash(data):
    empty = data["demand"].iloc[0:0]
    res = simulate(empty, data["inventory"])
    assert res["fill_rate"] == 1.0


def test_conflicting_agents_are_bounded(data):
    v = Validator(data["suppliers"], data["warehouses"], data["constraints"])
    c = Coordinator(v, ConflictResolver(capacity=450))
    out = c.coordinate([
        _rec("inventory", "transfer", "S2", "DC", 500),
        _rec("logistics", "expedite", "S2", "DC", 300),
    ])
    total = sum(r.recommendation.quantity for r in out["accepted"])
    assert total <= 450


def test_validator_blocks_oversized_then_coordinator_excludes(data):
    v = Validator(data["suppliers"], data["warehouses"], data["constraints"])
    c = Coordinator(v, ConflictResolver())
    out = c.coordinate([_rec("supplier_risk", "alternate_source", "S2", "DC", 99999)])
    assert out["accepted"] == []
    assert out["rejected"][0]["agent"] == "supplier_risk"


def test_milp_handles_more_disruption_without_exception(data):
    disruption = {"supplier": "S1", "start": 1, "duration": 30}
    res = solve(data["demand"], data["suppliers"], scenario=disruption)
    assert res["status"] in ("Optimal", "Feasible")
    assert res["backorders"] > 0


def test_agents_never_write_data(data):
    """Governance: agent outputs are pure Recommendations, not mutations."""
    before = data["inventory"].copy(deep=True)
    from agents.inventory_agent import InventoryAgent
    InventoryAgent(data["inventory"], data["warehouses"]).run("S1_DISRUPTION_01")
    pd.testing.assert_frame_equal(before, data["inventory"])
