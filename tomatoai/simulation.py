"""Provider-neutral deterministic simulation contracts for TomatoAI."""
from typing import Any, Protocol


class Simulator(Protocol):
    def reset(self) -> dict[str, Any]:
        ...

    def step(self, action: Any) -> dict[str, Any]:
        ...

    def close(self) -> None:
        ...


class DryRunSimulator:
    """Dependency-free simulator for pipeline and integration smoke tests."""

    def __init__(self) -> None:
        self.step_count = 0
        self.last_action: Any = None
        self.closed = False

    def reset(self) -> dict[str, Any]:
        self.step_count = 0
        self.last_action = None
        self.closed = False
        return {"step": 0, "status": "ready"}

    def step(self, action: Any) -> dict[str, Any]:
        if self.closed:
            raise RuntimeError("simulator is closed")
        self.step_count += 1
        self.last_action = action
        return {"step": self.step_count, "status": "ok", "action": action}

    def close(self) -> None:
        self.closed = True


class TomatoSimulation:
    """Small deterministic tomato environment for repeatable development tests.

    It intentionally models only stable interfaces: plant count, fruit count,
    ripeness, temperature, and irrigation. It is not a biological simulator.
    """

    def __init__(self, *, plants: int = 10, seed: int = 0) -> None:
        if plants < 0:
            raise ValueError("plants must be non-negative")
        self.plants = plants
        self.seed = seed
        self.step_count = 0
        self.closed = False
        self._fruit_count = plants * 2
        self._ripeness = 0.0
        self._temperature = 24.0
        self._irrigation = 0.0

    def reset(self) -> dict[str, Any]:
        self.step_count = 0
        self.closed = False
        self._fruit_count = self.plants * 2
        self._ripeness = 0.0
        self._temperature = 24.0
        self._irrigation = 0.0
        return self.state()

    def state(self) -> dict[str, Any]:
        return {
            "step": self.step_count,
            "plants": self.plants,
            "fruit_count": self._fruit_count,
            "ripeness": round(self._ripeness, 6),
            "temperature_c": round(self._temperature, 6),
            "irrigation": round(self._irrigation, 6),
            "closed": self.closed,
        }

    def step(self, action: Any = None) -> dict[str, Any]:
        if self.closed:
            raise RuntimeError("simulator is closed")
        if action is not None and not isinstance(action, dict):
            raise ValueError("action must be a mapping or None")
        action = action or {}
        self._temperature = float(action.get("temperature_c", self._temperature))
        self._irrigation = max(0.0, min(1.0, float(action.get("irrigation", 0.0))))
        self._ripeness = min(1.0, self._ripeness + 0.01 + self._irrigation * 0.005)
        self.step_count += 1
        return self.state()

    def close(self) -> None:
        self.closed = True
