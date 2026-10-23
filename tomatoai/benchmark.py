"""Small, deterministic benchmarking primitives for TomatoAI components."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Callable, Sequence, TypeVar

from tomatoai.evaluation import classification_accuracy, mean_iou

T = TypeVar("T")


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    predicted: object
    expected: object


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    count: int
    score: float
    passed: bool


def run_classification_benchmark(
    name: str, cases: Sequence[BenchmarkCase], *, threshold: float = 1.0
) -> BenchmarkResult:
    if not cases:
        raise ValueError("benchmark requires at least one case")
    score = classification_accuracy(
        [str(case.predicted) for case in cases],
        [str(case.expected) for case in cases],
    )
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0, 1]")
    return BenchmarkResult(name, len(cases), score, score >= threshold)


def run_iou_benchmark(
    name: str, cases: Sequence[BenchmarkCase], *, threshold: float = 1.0
) -> BenchmarkResult:
    if not cases:
        raise ValueError("benchmark requires at least one case")
    score = mean_iou(
        [set(case.predicted) for case in cases],
        [set(case.expected) for case in cases],
    )
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0, 1]")
    return BenchmarkResult(name, len(cases), score, score >= threshold)


def aggregate_scores(results: Sequence[BenchmarkResult]) -> float:
    if not results:
        raise ValueError("at least one benchmark result is required")
    return mean(result.score for result in results)


def evaluate_cases(cases: Sequence[T], evaluator: Callable[[T], float]) -> float:
    if not cases:
        raise ValueError("at least one case is required")
    scores = [float(evaluator(case)) for case in cases]
    if any(not 0.0 <= score <= 1.0 for score in scores):
        raise ValueError("case scores must be in [0, 1]")
    return mean(scores)
