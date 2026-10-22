"""Evaluation primitives for TomatoAI perception outputs."""
from collections import Counter


def classification_accuracy(predicted: list[str], expected: list[str]) -> float:
    if len(predicted) != len(expected):
        raise ValueError("prediction and target lengths must match")
    if not expected:
        return 0.0
    return sum(a == b for a, b in zip(predicted, expected)) / len(expected)


def mean_iou(predicted: list[set[int]], expected: list[set[int]]) -> float:
    if len(predicted) != len(expected):
        raise ValueError("prediction and target lengths must match")
    if not predicted:
        return 0.0
    scores = []
    for pred, target in zip(predicted, expected):
        union = pred | target
        scores.append(1.0 if not union else len(pred & target) / len(union))
    return sum(scores) / len(scores)


def confusion_counts(predicted: list[str], expected: list[str]) -> dict[str, dict[str, int]]:
    if len(predicted) != len(expected):
        raise ValueError("prediction and target lengths must match")
    labels = sorted(set(predicted) | set(expected))
    counts = {label: {other: 0 for other in labels} for label in labels}
    for pred, target in zip(predicted, expected):
        counts[target][pred] += 1
    return counts
