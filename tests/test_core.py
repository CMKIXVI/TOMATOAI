from datetime import datetime, timezone

import pytest

from tomatoai.plant_state import Confidence, FruitState, PlantState
from tomatoai.safety import validate_confidence, validate_scalar_limits


def test_confidence_range():
    assert validate_confidence(0.0)
    assert validate_confidence(1.0)
    assert not validate_confidence(1.1)


def test_confidence_object_rejects_invalid_value():
    with pytest.raises(ValueError):
        Confidence(1.2)


def test_plant_state_serializes_without_guessing_missing_environment():
    state = PlantState(
        plant_id="row-01-plant-01",
        observed_at=datetime.now(timezone.utc),
        fruit=FruitState(visible_count=3, ripe_count=1),
        environment={"air_temperature_c": None},
        uncertainty_flags=["environment_readings_missing"],
    )
    payload = state.to_dict()
    assert payload["plant_id"] == "row-01-plant-01"
    assert payload["environment"]["air_temperature_c"] is None


def test_scalar_limits():
    limits = {"linear_speed": (0.0, 0.2)}
    assert validate_scalar_limits({"linear_speed": 0.1}, limits)
    assert not validate_scalar_limits({"linear_speed": 0.3}, limits)
