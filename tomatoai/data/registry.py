"""Dataset registry with explicit task/role filtering."""
from pathlib import Path

from .manifest import DatasetManifest, load_manifest


class DatasetRegistry:
    def __init__(self, manifest_path: str | Path):
        self.datasets = load_manifest(manifest_path)

    def get(self, dataset_id: str) -> DatasetManifest:
        for dataset in self.datasets:
            if dataset.dataset_id == dataset_id:
                return dataset
        raise KeyError(dataset_id)

    def by_role(self, role: str) -> list[DatasetManifest]:
        return [dataset for dataset in self.datasets if dataset.role == role]

    def by_modality(self, modality: str) -> list[DatasetManifest]:
        return [dataset for dataset in self.datasets if modality in dataset.modalities]

    def summary(self) -> dict[str, int]:
        return {
            "datasets": len(self.datasets),
            "perception": len(self.by_role("perception")),
            "temporal": len(self.by_role("temporal")),
            "robotics": len(self.by_role("robotics")),
            "agronomic": len(self.by_role("agronomic")),
        }
