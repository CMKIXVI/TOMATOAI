"""Normalized action records for robot demonstration datasets."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ActionStep:
    timestamp: float
    joint_positions: tuple[float, ...] = ()
    joint_velocities: tuple[float, ...] = ()
    gripper: float | None = None
    frame_id: str | None = None

    def validate(self) -> None:
        if self.timestamp < 0:
            raise ValueError("timestamp must be non-negative")
        if not self.joint_positions and not self.frame_id:
            raise ValueError("an action step needs joint positions or a frame reference")
        if self.gripper is not None and not 0.0 <= self.gripper <= 1.0:
            raise ValueError("gripper must be in [0, 1]")


@dataclass
class ActionEpisode:
    episode_id: str
    dataset: str
    steps: list[ActionStep] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.episode_id or not self.dataset:
            raise ValueError("episode_id and dataset are required")
        if not self.steps:
            raise ValueError("episode must contain action steps")
        previous = -1.0
        for step in self.steps:
            step.validate()
            if step.timestamp < previous:
                raise ValueError("action timestamps must be monotonic")
            previous = step.timestamp
