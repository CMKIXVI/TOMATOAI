"""Provider-neutral temporal aggregation interface for tomato state."""
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Observation:
    timestamp: str
    perception: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class TemporalState:
    timestamp: str
    growth_stage: str | None
    fruit_count: int | None
    ripeness_distribution: dict[str, float]
    stress_indicators: dict[str, float]
    confidence: float


class TemporalStateEstimator(Protocol):
    def update(self, observations: list[Observation]) -> TemporalState:
        """Estimate plant state from an ordered observation history."""
        ...


def validate_state(state: TemporalState) -> None:
    if not 0.0 <= state.confidence <= 1.0:
        raise ValueError("confidence must be in [0, 1]")
    if state.fruit_count is not None and state.fruit_count < 0:
        raise ValueError("fruit_count must be non-negative")
    for name, value in state.ripeness_distribution.items():
        if value < 0:
            raise ValueError(f"negative ripeness value: {name}")
