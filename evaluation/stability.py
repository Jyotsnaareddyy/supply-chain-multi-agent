"""Recommendation stability: run the same scenario N times, compare decisions."""
from __future__ import annotations


def stability(runs: list[dict]) -> dict:
    actions = [tuple(sorted(r.keys())) for r in runs]
    unique = len(set([str(a) for a in actions]))
    return {"runs": len(runs), "unique_decision_sets": unique}
