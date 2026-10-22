import pytest
from tomatoai.temporal_estimator import estimate_temporal_state
from tomatoai.temporal_state import Observation


def obs(i, **perception):
    return Observation(f"2026-10-23T00:00:{i:02d}Z", perception=perception)


@pytest.mark.parametrize("index", range(120))
def test_temporal_sequences_are_deterministic(index):
    count = index % 20
    state = estimate_temporal_state([
        obs(0, fruit_count=max(0, count - 1), growth_stage="vegetative"),
        obs(1, fruit_count=count, growth_stage="flowering", ripeness_distribution={"green": 1.0}),
    ])
    assert state.timestamp.endswith("01Z")
    assert state.fruit_count == count
    assert state.growth_stage in {"vegetative", "flowering"}
    assert state.confidence == 1.0


@pytest.mark.parametrize("count", [0, 1, 2, 5, 10, 25, 100])
def test_latest_valid_fruit_count_is_selected(count):
    state = estimate_temporal_state([obs(0, fruit_count=1), obs(1, fruit_count=count)])
    assert state.fruit_count == count


@pytest.mark.parametrize("stage", ["seedling", "vegetative", "flowering", "fruiting", "mature"])
def test_growth_stage_is_derived(stage):
    state = estimate_temporal_state([obs(0, growth_stage=stage)])
    assert state.growth_stage == stage


@pytest.mark.parametrize("value", [0.0, 0.1, 0.5, 0.9, 1.0, 10.0])
def test_ripeness_values_are_preserved(value):
    state = estimate_temporal_state([obs(0, ripeness_distribution={"ripe": value})])
    assert state.ripeness_distribution["ripe"] == value


@pytest.mark.parametrize("value", [0.0, 0.1, 0.5, 1.0, 5.0])
def test_stress_values_are_preserved(value):
    state = estimate_temporal_state([obs(0, stress_indicators={"water_stress": value})])
    assert state.stress_indicators["water_stress"] == value


def test_empty_history_is_rejected():
    with pytest.raises(ValueError, match="at least one"):
        estimate_temporal_state([])


def test_unordered_history_is_rejected():
    with pytest.raises(ValueError, match="ordered"):
        estimate_temporal_state([obs(2, fruit_count=2), obs(1, fruit_count=1)])


def test_missing_perception_reduces_confidence():
    state = estimate_temporal_state([obs(0), obs(1, fruit_count=2)])
    assert state.confidence == 0.5


def test_invalid_boolean_fruit_count_is_ignored():
    state = estimate_temporal_state([obs(0, fruit_count=True), obs(1, fruit_count=4)])
    assert state.fruit_count == 4


def test_latest_ripeness_distribution_wins():
    state = estimate_temporal_state([
        obs(0, ripeness_distribution={"green": 1.0}),
        obs(1, ripeness_distribution={"ripe": 0.75}),
    ])
    assert state.ripeness_distribution == {"ripe": 0.75}


def test_latest_stress_indicators_win():
    state = estimate_temporal_state([
        obs(0, stress_indicators={"heat": 0.2}),
        obs(1, stress_indicators={"heat": 0.8}),
    ])
    assert state.stress_indicators == {"heat": 0.8}
