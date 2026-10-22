import pytest

from tomatoai.simulation import DryRunSimulator, TomatoSimulation


@pytest.mark.parametrize("index", range(120))
def test_tomato_simulation_repeated_steps_are_deterministic(index):
    sim = TomatoSimulation(plants=index % 21, seed=index)
    initial = sim.reset()
    assert initial["plants"] == index % 21
    assert initial["fruit_count"] == (index % 21) * 2
    result = sim.step({"irrigation": (index % 11) / 10.0})
    assert result["step"] == 1
    assert 0.0 <= result["ripeness"] <= 1.0
    assert 0.0 <= result["irrigation"] <= 1.0
    assert result["temperature_c"] == 24.0


@pytest.mark.parametrize("irrigation", [-10.0, -1.0, 0.0, 0.25, 0.5, 0.75, 1.0, 2.0, 10.0])
def test_irrigation_is_clamped(irrigation):
    sim = TomatoSimulation(plants=3)
    result = sim.step({"irrigation": irrigation})
    assert 0.0 <= result["irrigation"] <= 1.0


@pytest.mark.parametrize("temperature", [-20.0, 0.0, 10.0, 20.0, 24.0, 30.0, 40.0, 60.0])
def test_temperature_is_recorded(temperature):
    sim = TomatoSimulation(plants=2)
    result = sim.step({"temperature_c": temperature})
    assert result["temperature_c"] == temperature


def test_reset_restores_initial_state():
    sim = TomatoSimulation(plants=5)
    sim.step({"irrigation": 1.0, "temperature_c": 35.0})
    restored = sim.reset()
    assert restored["step"] == 0
    assert restored["fruit_count"] == 10
    assert restored["ripeness"] == 0.0
    assert restored["temperature_c"] == 24.0
    assert restored["irrigation"] == 0.0


def test_closed_simulation_rejects_steps():
    sim = TomatoSimulation()
    sim.close()
    with pytest.raises(RuntimeError, match="closed"):
        sim.step()


def test_invalid_action_type_is_rejected():
    sim = TomatoSimulation()
    with pytest.raises(ValueError, match="mapping"):
        sim.step("inspect")


def test_dry_run_contract_remains_compatible():
    sim = DryRunSimulator()
    assert sim.reset()["status"] == "ready"
    result = sim.step({"task": "inspect"})
    assert result["step"] == 1
    assert result["status"] == "ok"
    sim.close()
    with pytest.raises(RuntimeError):
        sim.step({"task": "inspect"})
