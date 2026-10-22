"""Thin provider adapter for an injected open VLA backend.

TomatoAI does not depend on a specific VLA package here. A backend only needs
``load``, ``predict`` and optionally ``metadata``; this keeps model selection
separate from the execution pipeline.
"""
from typing import Any, Protocol

from tomatoai.vla_adapter import VLAAdapter


class OpenVLABackend(Protocol):
    def load(self, config: dict[str, Any]) -> None: ...
    def predict(self, observation: Any) -> Any: ...

    def metadata(self) -> dict[str, Any]: ...


class OpenVLAAdapter(VLAAdapter):
    """Adapter that delegates inference to a caller-supplied backend."""

    def __init__(self, backend: OpenVLABackend) -> None:
        self.backend = backend
        self.config: dict[str, Any] = {}

    def load(self, config: dict[str, Any]) -> None:
        self.config = dict(config)
        self.backend.load(self.config)

    def prepare_observation(
        self,
        *,
        rgb: Any,
        depth: Any | None,
        robot_state: dict[str, Any],
        tomato_state: dict[str, Any],
        task: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "rgb": rgb,
            "depth": depth,
            "robot_state": robot_state,
            "tomato_state": tomato_state,
            "task": task,
        }

    def propose_action(self, observation: Any) -> Any:
        return self.backend.predict(observation)

    def decode_action(self, output: Any) -> dict[str, Any]:
        if not isinstance(output, dict):
            raise TypeError("VLA backend output must be a dict")
        return dict(output)

    def metadata(self) -> dict[str, Any]:
        return dict(self.backend.metadata())
