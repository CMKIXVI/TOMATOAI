from pathlib import Path

from tomatoai.data.canonical import CanonicalSample
from tomatoai.data.ingest import write_jsonl
from tomatoai.data.split import assign_groups, stable_group_split
from tomatoai.perception_metrics import f1_score, iou, precision_recall


def test_jsonl_roundtrip(tmp_path: Path):
    target = tmp_path / "samples.jsonl"
    count = write_jsonl([CanonicalSample("s1", "train", labels={"tomato": True})], target)
    assert count == 1
    assert target.read_text(encoding="utf-8").count("s1") == 1


def test_split_is_stable():
    assert stable_group_split("plant-17", {"train": 0.8, "validation": 0.1, "test": 0.1}) == stable_group_split(
        "plant-17", {"train": 0.8, "validation": 0.1, "test": 0.1}
    )
    assert set(assign_groups(["a", "b", "a"], {"train": 0.8, "test": 0.2})) <= {"a": "train", "b": "train"}.keys()


def test_metrics():
    precision, recall = precision_recall(8, 2, 2)
    assert round(precision, 3) == round(0.8, 3)
    assert round(recall, 3) == round(0.8, 3)
    assert round(f1_score(precision, recall), 3) == 0.8
    assert iou((0, 0, 2, 2), (1, 1, 3, 3)) == 1 / 7
