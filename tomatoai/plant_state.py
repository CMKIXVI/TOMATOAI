"""Small, model-independent plant-state contracts for TomatoAI.

This module deliberately contains data contracts rather than a trained model.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Confidence:
    value: float | None = None

    def __post_init__(self) -> None:
        if self.value is not None and not 0.0 <= self.value <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass
class FruitState:
    visible_count: int | None = None
    green_count: int | None = None
    turning_count: int | None = None
    ripe_count: int | None = None


@dataclass
class PlantState:
    plant_id: str | None
    observed_at: datetime
    growth_stage: str | None = None
    growth_confidence: Confidence = field(default_factory=Confidence)
    fruit: FruitState = field(default_factory=FruitState)
    environment: dict[str, float | None] = field(default_factory=dict)
    health_flags: list[dict[str, Any]] = field(default_factory=list)
    predictions: list[dict[str, Any]] = field(default_factory=list)
    uncertainty_flags: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "0.1.0",
            "plant_id": self.plant_id,
            "observed_at": self.observed_at.isoformat(),
            "observations": {
                "growth_stage": {
                    "value": self.growth_stage,
                    "confidence": self.growth_confidence.value,
                },
                "fruit": {
                    "visible_count": self.fruit.visible_count,
                    "green_count": self.fruit.green_count,
                    "turning_count": self.fruit.turning_count,
                    "ripe_count": self.fruit.ripe_count,
                },
                "health_flags": self.health_flags,
            },
            "environment": self.environment,
            "predictions": self.predictions,
            "uncertainty_flags": self.uncertainty_flags,
            "provenance": self.provenance,
        }
