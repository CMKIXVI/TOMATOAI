"""Typed access to the dataset registry YAML files."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    name: str
    role: str
    source: str
    license: str | None = None
    modalities: tuple[str, ...] = ()
    notes: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def load_manifest(path: str | Path) -> list[DatasetManifest]:
    """Load datasets.yaml and return normalized dataset entries."""
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    entries = payload.get("datasets", [])
    manifests: list[DatasetManifest] = []
    for item in entries:
        known = {"id", "name", "role", "source", "license", "modalities", "notes"}
        manifests.append(
            DatasetManifest(
                dataset_id=item["id"],
                name=item["name"],
                role=item["role"],
                source=item["source"],
                license=item.get("license"),
                modalities=tuple(item.get("modalities", [])),
                notes=item.get("notes"),
                extra={k: v for k, v in item.items() if k not in known},
            )
        )
    return manifests
