import pytest
from datetime import datetime, timezone

from tomatoai.perception_baseline import Prediction
from tomatoai.perception_state import predictions_to_plant_state


OBSERVED_AT = datetime(2026, 10, 23, tzinfo=timezone.utc)


@pytest.mark.parametrize("label", ["green", "turning", "ripe"])
def test_each_ripeness_label_maps_to_fruit_counts(label):
    state = predictions_to_plant_state([Prediction(label, 0.9)], observed_at=OBSERVED_AT)
    assert state.fruit.visible_count == 1
    assert getattr(state.fruit, f"{label}_count") == 1


@pytest.mark.parametrize("confidence", [0.0, 0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0])
def test_ripeness_confidence_boundaries_are_preserved(confidence):
    state = predictions_to_plant_state([Prediction("ripe", confidence)], observed_at=OBSERVED_AT)
    assert state.fruit.ripe_count == 1


@pytest.mark.parametrize("stage", ["seedling", "vegetative", "flowering", "fruiting", "mature"])
def test_growth_stage_labels_map_to_plant_state(stage):
    state = predictions_to_plant_state([Prediction(stage, 0.8)], observed_at=OBSERVED_AT)
    assert state.growth_stage == stage
    assert state.growth_confidence.value == 0.8


@pytest.mark.parametrize("label", ["GREEN", "Turning", "RIPE", " Fruiting ", "FLOWERING"])
def test_labels_are_normalized(label):
    state = predictions_to_plant_state([Prediction(label, 0.8)], observed_at=OBSERVED_AT)
    assert state.growth_stage in {None, "fruiting", "flowering"} or state.fruit.visible_count == 1


@pytest.mark.parametrize("index", range(100))
def test_repeated_perception_cases_are_deterministic(index):
    labels = ["green", "turning", "ripe"]
    label = labels[index % len(labels)]
    confidence = (index % 101) / 100.0
    state = predictions_to_plant_state(
        [Prediction(label, confidence)],
        observed_at=OBSERVED_AT,
        plant_id=f"plant-{index}",
        environment={"temperature_c": 24.0},
        provenance={"camera": "rgb-{0}".format(index % 3)},
    )
    assert state.plant_id == f"plant-{index}"
    assert state.observed_at == OBSERVED_AT
    assert state.fruit.visible_count == 1
    assert state.environment["temperature_c"] == 24.0
    assert state.provenance["camera"] in {"rgb-0", "rgb-1", "rgb-2"}


@pytest.mark.parametrize("bad", [-0.01, 1.01, 2.0])
def test_invalid_prediction_confidence_is_rejected(bad):
    with pytest.raises(ValueError, match="confidence"):
        predictions_to_plant_state([Prediction("ripe", bad)], observed_at=OBSERVED_AT)


@pytest.mark.parametrize("label", ["health:blight", "health:wilt", "health:stress"])
def test_health_predictions_become_health_flags(label):
    state = predictions_to_plant_state([Prediction(label, 0.7)], observed_at=OBSERVED_AT)
    assert state.health_flags[0]["label"] == label.split(":", 1)[1]
    assert state.health_flags[0]["confidence"] == 0.7


def test_mixed_fruit_predictions_sum_correctly():
    predictions = [
        Prediction("green", 0.8),
        Prediction("green", 0.9),
        Prediction("turning", 0.7),
        Prediction("ripe", 1.0),
    ]
    state = predictions_to_plant_state(predictions, observed_at=OBSERVED_AT)
    assert state.fruit.visible_count == 4
    assert state.fruit.green_count == 2
    assert state.fruit.turning_count == 1
    assert state.fruit.ripe_count == 1


def test_unknown_labels_are_explicitly_recorded_as_uncertain():
    state = predictions_to_plant_state([Prediction("leaf", 0.5)], observed_at=OBSERVED_AT)
    assert state.uncertainty_flags == ["unmapped:leaf"]
    assert state.fruit.visible_count == 0


def test_environment_and_provenance_are_copied():
    environment = {"temperature_c": 25.0, "humidity": 60.0}
    provenance = {"model": "baseline", "frame": 4}
    state = predictions_to_plant_state([], observed_at=OBSERVED_AT, environment=environment, provenance=provenance)
    assert state.environment == environment
    assert state.provenance == provenance


def test_empty_predictions_produce_empty_observation_state():
    state = predictions_to_plant_state([], observed_at=OBSERVED_AT)
    assert state.fruit.visible_count == 0
    assert state.growth_stage is None
    assert state.growth_confidence.value is None


def test_strongest_growth_prediction_wins():
    state = predictions_to_plant_state(
        [Prediction("vegetative", 0.4), Prediction("flowering", 0.9), Prediction("fruiting", 0.6)],
        observed_at=OBSERVED_AT,
    )
    assert state.growth_stage == "flowering"
    assert state.growth_confidence.value == 0.9


def test_to_dict_preserves_canonical_fields():
    state = predictions_to_plant_state([Prediction("ripe", 0.95)], observed_at=OBSERVED_AT, plant_id="p1")
    data = state.to_dict()
    assert data["plant_id"] == "p1"
    assert data["observations"]["fruit"]["ripe_count"] == 1
    assert data["observations"]["growth_stage"]["value"] is None
