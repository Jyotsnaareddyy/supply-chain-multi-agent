"""Demand agent: proposes demand/allocation changes. Read-only on data."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from schemas.recommendation import Recommendation, RecommendationPayload


class DemandAgent:
    def __init__(self, demand: pd.DataFrame, customers: pd.DataFrame):
        self.demand = demand
        self.customers = customers

    def run(self, scenario_id: str) -> Recommendation:
        avg = self.demand.groupby("customer_id")["demand"].mean()
        high_priority = self.customers.set_index("customer_id")["priority"]
        # Propose increasing allocation to high-priority customers.
        target = avg.index[high_priority.reindex(avg.index) == "high"][0]
        return Recommendation(
            scenario_id=scenario_id,
            agent="demand",
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommendation=RecommendationPayload(
                action="increase_allocation",
                destination=target,
                parameters={"horizon_days": 30},
            ),
            confidence=0.85,
            reason="High-priority customers drive most of forecast demand.",
            constraints_checked=["demand_forecast"],
        )
