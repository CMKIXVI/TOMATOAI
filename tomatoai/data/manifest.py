"""Typed access to the dataset registry YAML files."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    name: str
    roles: tuple[str, ...]
    source: str
    license: str | None = None
    modalities: tuple[str, ...] = ()
    notes: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def role(self) -> str:
        return self.roles[0] if self.roles else ""


def load_manifest(path: str | Path) -> list[DatasetManifest]:
    """Load the repository dataset registry and normalize its source entries."""
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    entries = payload.get("sources", payload.get("datasets", []))
    manifests: list[DatasetManifest] = []
    for item in entries:
        known = {"id", "name", "role", "roles", "source", "source_url", "license", "license_note", "modalities", "notes"}
        raw_roles = item.get("roles", item.get("role", []))
        if isinstance(raw_roles, str):
            raw_roles = [raw_roles]
        manifests.append(
            DatasetManifest(
                dataset_id=item["id"],
                name=item["name"],
                roles=tuple(raw_roles),
                source=item.get("source", item.get("source_url", "")),
                license=item.get("license", item.get("license_note")),
                modalities=tuple(item.get("modalities", [])),
                notes=item.get("notes", item.get("license_note")),
                extra={k: v for k, v in item.items() if k not in known},
            )
        )
    return manifests
