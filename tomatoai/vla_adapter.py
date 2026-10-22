"""Provider-neutral VLA adapter contract.

A concrete adapter should translate TomatoAI observations/tasks into the
selected open-weight VLA's native format. The VLA only proposes actions;
robot safety and motion validation remain outside this interface.
"""
from abc import ABC, abstractmethod
from typing import Any


class VLAAdapter(ABC):
    @abstractmethod
    def load(self, config: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def prepare_observation(
        self,
        *,
        rgb: Any,
        depth: Any | None,
        robot_state: dict[str, Any],
        tomato_state: dict[str, Any],
        task: dict[str, Any],
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    def propose_action(self, observation: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def decode_action(self, output: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        raise NotImplementedError
