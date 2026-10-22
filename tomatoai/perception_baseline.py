"""Dependency-light baseline perception model.

This is a deterministic reference implementation for pipeline validation, not the
production vision model. A real encoder/detector can implement the same contract.
"""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Prediction:
    label: str
    confidence: float
    bbox: tuple[float, float, float, float] | None = None


class BaselinePerception:
    """Contract-compatible baseline that consumes precomputed candidates."""

    def predict(self, candidates: list[dict[str, Any]]) -> list[Prediction]:
        results = []
        for item in candidates:
            confidence = float(item.get("confidence", 0.0))
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("confidence must be between 0 and 1")
            bbox = item.get("bbox")
            results.append(Prediction(str(item["label"]), confidence, tuple(bbox) if bbox else None))
        return results
