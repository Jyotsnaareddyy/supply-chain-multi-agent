"""Resolve conflicting recommendations (e.g. transfer vs transport capacity)."""
from __future__ import annotations

from collections import defaultdict

from schemas.recommendation import Recommendation


class ConflictResolver:
    """Caps quantities when multiple agents target the same route/resource."""

    def __init__(self, capacity: float = 300):
        self.capacity = capacity

    def resolve(self, recs: list[Recommendation], capacity: float | None = None) -> list[Recommendation]:
        capacity = self.capacity if capacity is None else capacity
        totals: dict[str, float] = defaultdict(float)
        resolved = []
        for rec in recs:
            key = f"{rec.recommendation.source}->{rec.recommendation.destination}"
            qty = rec.recommendation.quantity or 0
            if totals[key] + qty <= capacity:
                totals[key] += qty
                resolved.append(rec)
            else:
                allowed = max(0, capacity - totals[key])
                if allowed > 0:
                    rec.recommendation.quantity = allowed
                    rec.reason += f" (capped to {allowed} by coordinator)"
                    totals[key] += allowed
                    resolved.append(rec)
        return resolved
