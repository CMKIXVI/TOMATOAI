import pytest

from tomatoai.benchmark import (
    BenchmarkCase,
    aggregate_scores,
    evaluate_cases,
    run_classification_benchmark,
    run_iou_benchmark,
)


@pytest.mark.parametrize("index", range(120))
def test_classification_benchmark_perfect_cases(index):
    case = BenchmarkCase(f"cls-{index}", "ripe", "ripe")
    result = run_classification_benchmark(f"classification-{index}", [case])
    assert result.count == 1
    assert result.score == 1.0
    assert result.passed


@pytest.mark.parametrize("index", range(120))
def test_iou_benchmark_perfect_cases(index):
    expected = {index % 5, (index + 1) % 5}
    case = BenchmarkCase(f"iou-{index}", expected, expected)
    result = run_iou_benchmark(f"iou-{index}", [case])
    assert result.count == 1
    assert result.score == 1.0
    assert result.passed


@pytest.mark.parametrize("threshold", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_classification_threshold_is_applied(threshold):
    cases = [
        BenchmarkCase("a", "ripe", "ripe"),
        BenchmarkCase("b", "green", "ripe"),
    ]
    result = run_classification_benchmark("threshold", cases, threshold=threshold)
    assert result.score == 0.5
    assert result.passed is (0.5 >= threshold)


@pytest.mark.parametrize("threshold", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_iou_threshold_is_applied(threshold):
    cases = [BenchmarkCase("a", {1, 2}, {1, 2})]
    result = run_iou_benchmark("threshold", cases, threshold=threshold)
    assert result.score == 1.0
    assert result.passed


def test_aggregate_scores_is_deterministic():
    a = run_classification_benchmark("a", [BenchmarkCase("1", "x", "x")])
    b = run_classification_benchmark(
        "b", [BenchmarkCase("1", "x", "y"), BenchmarkCase("2", "x", "x")]
    )
    assert aggregate_scores([a, b]) == 0.75


@pytest.mark.parametrize("index", range(20))
def test_evaluate_cases_accepts_normalized_scores(index):
    cases = list(range(5))
    score = evaluate_cases(cases, lambda value: ((value + index) % 5) / 4)
    assert 0.0 <= score <= 1.0


def test_empty_classification_benchmark_rejected():
    with pytest.raises(ValueError):
        run_classification_benchmark("empty", [])


def test_empty_iou_benchmark_rejected():
    with pytest.raises(ValueError):
        run_iou_benchmark("empty", [])


def test_empty_aggregate_rejected():
    with pytest.raises(ValueError):
        aggregate_scores([])


def test_empty_evaluation_rejected():
    with pytest.raises(ValueError):
        evaluate_cases([], lambda _: 1.0)


@pytest.mark.parametrize("threshold", [-0.1, 1.1])
def test_invalid_classification_threshold_rejected(threshold):
    with pytest.raises(ValueError):
        run_classification_benchmark(
            "invalid", [BenchmarkCase("1", "x", "x")], threshold=threshold
        )


@pytest.mark.parametrize("threshold", [-0.1, 1.1])
def test_invalid_iou_threshold_rejected(threshold):
    with pytest.raises(ValueError):
        run_iou_benchmark("invalid", [BenchmarkCase("1", {1}, {1})], threshold=threshold)


def test_iou_empty_sets_score_one():
    result = run_iou_benchmark("empty-mask", [BenchmarkCase("1", set(), set())])
    assert result.score == 1.0


def test_evaluation_rejects_out_of_range_scores():
    with pytest.raises(ValueError):
        evaluate_cases([1], lambda _: 1.1)
