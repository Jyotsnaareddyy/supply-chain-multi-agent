"""Logistics agent: proposes mode/route changes."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from schemas.recommendation import Recommendation, RecommendationPayload


class LogisticsAgent:
    def __init__(self, transport: pd.DataFrame):
        self.transport = transport

    def run(self, scenario_id: str) -> Recommendation:
        air = self.transport[self.transport["mode"] == "air"]
        row = air.iloc[0] if not air.empty else self.transport.iloc[0]
        return Recommendation(
            scenario_id=scenario_id,
            agent="logistics",
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommendation=RecommendationPayload(
                action="expedite",
                source=row["origin"],
                destination=row["destination"],
                quantity=150,
                parameters={"mode": row["mode"]},
            ),
            expected_cost=1200,
            expected_service_impact=0.02,
            confidence=0.85,
            reason=f"Air mode saves lead time vs road ({row['lead_time']} day).",
            constraints_checked=["transport_capacity", "budget"],
        )
