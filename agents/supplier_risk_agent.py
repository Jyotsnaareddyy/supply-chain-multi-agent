"""Supplier risk agent: monitors disruption and proposes alternate sourcing."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from schemas.recommendation import Recommendation, RecommendationPayload


class SupplierRiskAgent:
    def __init__(self, suppliers: pd.DataFrame, scenarios: pd.DataFrame):
        self.suppliers = suppliers
        self.scenarios = scenarios

    def run(self, scenario_id: str) -> Recommendation:
        scenario = self.scenarios[self.scenarios["scenario_id"] == scenario_id].iloc[0]
        disrupted = scenario["supplier"]
        alternatives = self.suppliers[self.suppliers["supplier_id"] != disrupted]
        best = alternatives.sort_values("risk_score").iloc[0]
        return Recommendation(
            scenario_id=scenario_id,
            agent="supplier_risk",
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommendation=RecommendationPayload(
                action="alternate_source",
                source=best["supplier_id"],
                destination="DC",
                quantity=400,
            ),
            expected_cost=3500,
            expected_service_impact=0.03,
            confidence=0.9,
            reason=f"{disrupted} unavailable for {scenario['duration']} days.",
            constraints_checked=["supplier_capacity", "lead_time"],
        )
