from evaluation.experiments import evaluate_scenario


def test_evaluate_scenario_returns_three_rows(data):
    sc = {"name": "S1-7D", "disruption": {"supplier": "S1", "start": 10, "duration": 7},
          "demand_mult": 1.0, "transport_mult": 1.0}
    rows, accepted, rejected = evaluate_scenario(
        sc, data["demand"], data["suppliers"], data["warehouses"], data["customers"],
        data["inventory"], data["scenarios"], data["constraints"], data["transport"],
    )
    assert {r["approach"] for r in rows} == {"milp", "multi_agent", "reorder_rule"}
    for r in rows:
        assert 0.0 <= r["fill_rate"] <= 1.0
        assert r["runtime_s"] >= 0
    assert len(accepted) >= 1
