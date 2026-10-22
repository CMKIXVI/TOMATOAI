"""Dataset registry with explicit task/role filtering."""
from pathlib import Path

from .manifest import DatasetManifest, load_manifest


ROLE_GROUPS = {
    "perception": {"detection", "segmentation", "depth_localization", "3d_segmentation", "ripeness", "fruit_counting", "skeletonisation", "phenotyping"},
    "temporal": {"growth", "environment", "greenhouse_monitoring", "climate", "greenhouse_control"},
    "robotics": {"robot_imitation", "pruning", "harvesting", "manipulation"},
    "agronomic": {"growth", "environment", "phenotype", "yield", "greenhouse_monitoring", "greenhouse_control", "irrigation", "climate", "harvest", "quality"},
}


class DatasetRegistry:
    def __init__(self, manifest_path: str | Path):
        self.datasets = load_manifest(manifest_path)

    def get(self, dataset_id: str) -> DatasetManifest:
        for dataset in self.datasets:
            if dataset.dataset_id == dataset_id:
                return dataset
        raise KeyError(dataset_id)

    def by_role(self, role: str) -> list[DatasetManifest]:
        if role in ROLE_GROUPS:
            return [dataset for dataset in self.datasets if set(dataset.roles) & ROLE_GROUPS[role]]
        return [dataset for dataset in self.datasets if role in dataset.roles]

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
