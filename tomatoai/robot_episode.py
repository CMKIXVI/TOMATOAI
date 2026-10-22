"""Canonical robot demonstration episode representation."""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ActionStep:
    timestamp: float
    joint_positions: tuple[float, ...] = ()
    gripper: float | None = None
    base_velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class RobotEpisode:
    episode_id: str
    observations: list[dict[str, Any]] = field(default_factory=list)
    actions: list[ActionStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.episode_id:
            raise ValueError("episode_id must not be empty")
        if len(self.observations) != len(self.actions):
            raise ValueError("observations and actions must have equal length")
