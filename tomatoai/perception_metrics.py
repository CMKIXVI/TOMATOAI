"""Small dependency-free metrics for TomatoAI perception baselines."""
from __future__ import annotations


def precision_recall(tp: int, fp: int, fn: int) -> tuple[float, float]:
    if min(tp, fp, fn) < 0:
        raise ValueError("counts must be non-negative")
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall


def f1_score(precision: float, recall: float) -> float:
    if not 0 <= precision <= 1 or not 0 <= recall <= 1:
        raise ValueError("precision and recall must be in [0, 1]")
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def iou(box_a: tuple[float, float, float, float], box_b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    if ax2 < ax1 or ay2 < ay1 or bx2 < bx1 or by2 < by1:
        raise ValueError("boxes must be x1,y1,x2,y2 with x2>=x1 and y2>=y1")
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    intersection = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - intersection
    return intersection / union if union else 0.0
