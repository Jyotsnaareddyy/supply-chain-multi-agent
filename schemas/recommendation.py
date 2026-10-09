"""Shared recommendation schema used by all agents."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, List, Optional


@dataclass
class RecommendationPayload:
    action: str
    source: Optional[str] = None
    destination: Optional[str] = None
    quantity: Optional[float] = None
    parameters: dict = field(default_factory=dict)


@dataclass
class Recommendation:
    scenario_id: str
    agent: str
    timestamp: str
    recommendation: RecommendationPayload
    expected_cost: float = 0.0
    expected_service_impact: float = 0.0
    confidence: float = 0.0
    reason: str = ""
    constraints_checked: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Recommendation":
        payload = RecommendationPayload(**data["recommendation"])
        return cls(
            scenario_id=data["scenario_id"],
            agent=data["agent"],
            timestamp=data["timestamp"],
            recommendation=payload,
            expected_cost=data.get("expected_cost", 0.0),
            expected_service_impact=data.get("expected_service_impact", 0.0),
            confidence=data.get("confidence", 0.0),
            reason=data.get("reason", ""),
            constraints_checked=data.get("constraints_checked", []),
        )
