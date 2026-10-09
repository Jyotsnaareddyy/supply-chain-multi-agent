from schemas.recommendation import Recommendation, RecommendationPayload
from coordinator.validator import Validator


def _rec(agent="supplier_risk", action="alternate_source", source="S2", destination="DC", quantity=100):
    return Recommendation(scenario_id="S", agent=agent, timestamp="t",
                          recommendation=RecommendationPayload(action=action, source=source, destination=destination, quantity=quantity))


def test_valid_rec_passes(data):
    v = Validator(data["suppliers"], data["warehouses"], data["constraints"])
    ok, msg = v.validate(_rec(quantity=100))
    assert ok, msg


def test_over_supplier_capacity_rejected(data):
    v = Validator(data["suppliers"], data["warehouses"], data["constraints"])
    ok, msg = v.validate(_rec(quantity=10_000))
    assert not ok and "capacity" in msg


def test_negative_quantity_rejected(data):
    v = Validator(data["suppliers"], data["warehouses"], data["constraints"])
    ok, _ = v.validate(_rec(quantity=-5))
    assert not ok


def test_expedite_cap_enforced(data):
    v = Validator(data["suppliers"], data["warehouses"], data["constraints"])
    max_exp = data["constraints"].iloc[0]["max_expedite"]
    ok, _ = v.validate(_rec(action="expedite", quantity=max_exp + 1))
    assert not ok
