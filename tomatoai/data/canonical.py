"""Canonical multimodal records used across TomatoAI datasets.

The canonical layer deliberately contains no dataset-specific assumptions. Adapters
convert source annotations into these records so training code can remain stable.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ImageRecord:
    path: str
    modality: str = "rgb"
    timestamp: str | None = None
    camera_id: str | None = None
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True)
class SensorRecord:
    timestamp: str
    values: dict[str, float]
    source: str | None = None


@dataclass
class CanonicalSample:
    sample_id: str
    split: str
    images: list[ImageRecord] = field(default_factory=list)
    sensors: list[SensorRecord] = field(default_factory=list)
    labels: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.sample_id:
            raise ValueError("sample_id must not be empty")
        if self.split not in {"train", "validation", "test", "eval"}:
            raise ValueError(f"unsupported split: {self.split}")
        if not self.images and not self.sensors and not self.labels:
            raise ValueError("sample must contain at least one data modality")
