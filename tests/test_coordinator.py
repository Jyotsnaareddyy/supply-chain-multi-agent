from coordinator.coordinator import Coordinator
from coordinator.conflict_resolver import ConflictResolver
from coordinator.validator import Validator
from schemas.recommendation import Recommendation, RecommendationPayload


def _rec(agent, action, source, destination, quantity):
    return Recommendation(scenario_id="S", agent=agent, timestamp="t",
                          recommendation=RecommendationPayload(action=action, source=source, destination=destination, quantity=quantity))


def test_mixed_valid_invalid(data):
    v = Validator(data["suppliers"], data["warehouses"], data["constraints"])
    c = Coordinator(v, ConflictResolver(capacity=450))
    out = c.coordinate([
        _rec("good", "alternate_source", "S2", "DC", 100),
        _rec("bad", "alternate_source", "S2", "DC", -1),
    ])
    assert len(out["accepted"]) == 1
    assert len(out["rejected"]) == 1
    assert out["rejected"][0]["agent"] == "bad"
