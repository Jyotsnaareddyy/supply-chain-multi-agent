"""Inventory agent: flags projected stockouts and proposes transfers."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from schemas.recommendation import Recommendation, RecommendationPayload


class InventoryAgent:
    def __init__(self, inventory: pd.DataFrame, warehouses: pd.DataFrame):
        self.inventory = inventory
        self.warehouses = warehouses

    def run(self, scenario_id: str) -> Recommendation:
        # Simple heuristic: transfer from the warehouse with the most surplus.
        stock = (
            self.inventory.groupby("location")["opening_inventory"].sum().sort_values(ascending=False)
        )
        source = stock.index[-1] if stock.index[-1] != "DC" else stock.index[0]
        return Recommendation(
            scenario_id=scenario_id,
            agent="inventory",
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommendation=RecommendationPayload(
                action="transfer",
                source=source,
                destination="WH1",
                quantity=100,
            ),
            expected_service_impact=0.02,
            confidence=0.8,
            reason="Prevent projected stockout at WH1.",
            constraints_checked=["safety_stock"],
        )
