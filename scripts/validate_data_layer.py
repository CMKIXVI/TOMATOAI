"""Validate the TomatoAI data layer without downloading datasets."""
from pathlib import Path

from tomatoai.data.registry import DatasetRegistry


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "datasets" / "manifests" / "datasets.yaml"


def main() -> int:
    registry = DatasetRegistry(MANIFEST)
    assert registry.datasets, "dataset registry is empty"
    assert registry.get("butom21").modalities
    assert registry.get("aerialyield-t2m").modalities
    assert registry.get("horti-m3-tomato").roles
    print("TomatoAI data layer OK")
    print(registry.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
