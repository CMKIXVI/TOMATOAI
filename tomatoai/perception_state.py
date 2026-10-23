"""Deterministic tomato perception-to-plant-state conversion.

The converter is intentionally model-independent: perception models emit normalized
predictions, while this layer turns them into the canonical PlantState contract.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from tomatoai.perception_baseline import Prediction
from tomatoai.plant_state import Confidence, FruitState, PlantState

RIPENESS_LABELS = {"green", "turning", "ripe"}
GROWTH_STAGES = {"seedling", "vegetative", "flowering", "fruiting", "mature"}


def predictions_to_plant_state(
    predictions: list[Prediction],
    *,
    observed_at: datetime,
    plant_id: str | None = None,
    environment: dict[str, float | None] | None = None,
    provenance: dict[str, Any] | None = None,
) -> PlantState:
    """Convert validated perception predictions into a deterministic PlantState."""
    fruit_counts = {label: 0 for label in RIPENESS_LABELS}
    growth_stage: str | None = None
    growth_confidence: float | None = None
    health_flags: list[dict[str, Any]] = []
    uncertainty: list[str] = []

    for prediction in predictions:
        if not 0.0 <= prediction.confidence <= 1.0:
            raise ValueError("prediction confidence must be between 0 and 1")
        label = prediction.label.strip().lower()
        if not label:
            raise ValueError("prediction label must not be empty")
        if label in RIPENESS_LABELS:
            fruit_counts[label] += 1
        elif label in GROWTH_STAGES:
            if growth_stage is None or prediction.confidence > (
                growth_confidence if growth_confidence is not None else -1.0
            ):
                growth_stage = label
                growth_confidence = prediction.confidence
        elif label.startswith("health:"):
            health_flags.append(
                {"label": label.split(":", 1)[1], "confidence": prediction.confidence}
            )
        else:
            uncertainty.append(f"unmapped:{label}")

    fruit_total = sum(fruit_counts.values())
    state = PlantState(
        plant_id=plant_id,
        observed_at=observed_at,
        growth_stage=growth_stage,
        growth_confidence=Confidence(growth_confidence),
        fruit=FruitState(
            visible_count=fruit_total,
            green_count=fruit_counts["green"],
            turning_count=fruit_counts["turning"],
            ripe_count=fruit_counts["ripe"],
        ),
        environment=dict(environment or {}),
        health_flags=health_flags,
        uncertainty_flags=uncertainty,
        provenance=dict(provenance or {}),
    )
    return state
