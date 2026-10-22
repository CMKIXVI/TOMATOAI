"""Minimal simulator contract and deterministic dry-run implementation."""
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
        return {
            "step": self.step_count,
            "status": "ok",
            "action": action,
        }

    def close(self) -> None:
        self.closed = True
