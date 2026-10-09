from schemas.recommendation import Recommendation, RecommendationPayload
from coordinator.conflict_resolver import ConflictResolver


def _rec(agent, quantity, source="S2", destination="DC"):
    return Recommendation(scenario_id="S", agent=agent, timestamp="t",
                          recommendation=RecommendationPayload(action="alternate_source", source=source, destination=destination, quantity=quantity))


def test_conflicting_routes_are_capped():
    recs = [_rec("a1", 400), _rec("a2", 150)]
    out = ConflictResolver(capacity=450).resolve(recs)
    total = sum(r.recommendation.quantity for r in out)
    assert total == 450
    assert len(out) == 2


def test_second_route_dropped_when_full():
    recs = [_rec("a1", 500), _rec("a2", 100)]
    out = ConflictResolver(capacity=450).resolve(recs)
    assert sum(r.recommendation.quantity for r in out) == 450
    assert out[0].recommendation.quantity == 450


def test_different_routes_not_limited():
    recs = [_rec("a1", 400, destination="DC"), _rec("a2", 300, source="WH3", destination="WH1")]
    out = ConflictResolver(capacity=450).resolve(recs)
    assert len(out) == 2
