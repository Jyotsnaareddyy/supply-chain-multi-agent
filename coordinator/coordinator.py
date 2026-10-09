"""Coordinator: collect -> validate -> resolve conflicts -> optimize -> approval."""
from __future__ import annotations

from schemas.recommendation import Recommendation

from .conflict_resolver import ConflictResolver
from .validator import Validator


class Coordinator:
    def __init__(self, validator: Validator, resolver: ConflictResolver | None = None):
        self.validator = validator
        self.resolver = resolver or ConflictResolver()

    def coordinate(self, recs: list[Recommendation]) -> dict:
        valid, rejected = [], []
        for rec in recs:
            ok, msg = self.validator.validate(rec)
            (valid if ok else rejected).append((rec, msg))

        resolved = self.resolver.resolve([r for r, _ in valid])
        return {
            "accepted": resolved,
            "rejected": [{"agent": r.agent, "reason": m} for r, m in rejected],
        }
