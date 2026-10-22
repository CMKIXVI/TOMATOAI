from pathlib import Path

from tomatoai.data.adapters import aerialyield_sample, butom21_sample
from tomatoai.data.canonical import CanonicalSample
from tomatoai.data.registry import DatasetRegistry


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_sample_validation():
    sample = CanonicalSample("x", "train", labels={"class": "tomato"})
    sample.validate()


def test_butom21_adapter():
    sample = butom21_sample("b1", "train", "rgb.png", "depth.png")
    assert [image.modality for image in sample.images] == ["rgb", "depth"]
    assert sample.metadata["dataset"] == "BUTom21"


def test_aerialyield_adapter():
    sample = aerialyield_sample("a1", "test", "frame.jpg", {"red": 2})
    assert sample.labels["ripeness"]["red"] == 2


def test_registry_loads_repo_manifest():
    registry = DatasetRegistry(ROOT / "datasets/manifests/datasets.yaml")
    assert registry.get("butom21").role == "perception"
    assert registry.get("horti-m3-tomato").role == "agronomic"
