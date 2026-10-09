from optimization.milp_model import solve


def test_optimal_without_disruption(data):
    res = solve(data["demand"], data["suppliers"], scenario=None)
    assert res["status"] in ("Optimal", "Feasible")
    assert res["backorders"] == 0


def test_disruption_creates_backorders(data):
    disruption = {"supplier": "S1", "start": 10, "duration": 7}
    res = solve(data["demand"], data["suppliers"], scenario=disruption)
    assert res["backorders"] > 0


def test_transport_multiplier_raises_cost(data):
    a = solve(data["demand"], data["suppliers"], scenario=None, transport_mult=1.0)
    b = solve(data["demand"], data["suppliers"], scenario=None, transport_mult=1.2)
    assert b["cost"] >= a["cost"]
