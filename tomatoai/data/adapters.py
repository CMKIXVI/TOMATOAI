"""Small source-format adapters.

These adapters normalize common annotation structures without copying raw datasets
into the repository. Large source data remains external and is referenced by path.
"""
from pathlib import Path
from typing import Any

from .canonical import CanonicalSample, ImageRecord


def image_sample(sample_id: str, split: str, image_path: str, labels: dict[str, Any] | None = None, **metadata: Any) -> CanonicalSample:
    sample = CanonicalSample(
        sample_id=sample_id,
        split=split,
        images=[ImageRecord(path=str(Path(image_path)), modality="rgb")],
        labels=labels or {},
        metadata=metadata,
    )
    sample.validate()
    return sample


def butom21_sample(sample_id: str, split: str, rgb_path: str, depth_path: str | None = None, labels: dict[str, Any] | None = None) -> CanonicalSample:
    """Normalize one BUTom21 RGB/depth sample."""
    images = [ImageRecord(path=rgb_path, modality="rgb")]
    if depth_path:
        images.append(ImageRecord(path=depth_path, modality="depth"))
    sample = CanonicalSample(sample_id, split, images=images, labels=labels or {}, metadata={"dataset": "BUTom21"})
    sample.validate()
    return sample


def aerialyield_sample(sample_id: str, split: str, image_path: str, ripeness_labels: dict[str, Any]) -> CanonicalSample:
    """Normalize an AerialYield-T2M image with six-stage ripeness annotations."""
    sample = CanonicalSample(
        sample_id=sample_id,
        split=split,
        images=[ImageRecord(path=image_path, modality="rgb")],
        labels={"ripeness": ripeness_labels},
        metadata={"dataset": "AerialYield-T2M"},
    )
    sample.validate()
    return sample
