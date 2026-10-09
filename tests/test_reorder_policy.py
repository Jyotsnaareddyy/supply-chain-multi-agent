from baselines.reorder_policy import simulate


def test_baseline_no_disruption_mostly_filled(data):
    res = simulate(data["demand"], data["inventory"], scenario=None)
    assert res["fill_rate"] > 0.95


def test_disruption_reduces_fill_rate(data):
    res = simulate(data["demand"], data["inventory"],
                   scenario={"supplier": "S1", "start": 10, "duration": 7})
    assert res["backorders"] > 0
    assert res["fill_rate"] < 1.0
