"""Provider-neutral perception contract.

Concrete models can be swapped without changing the plant-state or robot layers.
"""
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class TomatoInstance:
    instance_id: str
    bbox_xyxy: tuple[float, float, float, float]
    confidence: float
    ripeness: str | None = None
    mask: Any | None = None
    depth_m: float | None = None


@dataclass
class PerceptionResult:
    instances: list[TomatoInstance] = field(default_factory=list)
    plant_confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class PerceptionModel(Protocol):
    def predict(self, rgb: Any, depth: Any | None = None) -> PerceptionResult:
        """Return tomato/plant observations from one synchronized frame."""
