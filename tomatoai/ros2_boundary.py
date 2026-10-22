"""ROS 2-compatible integration boundary without requiring ROS at import time."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from tomatoai.robot_bridge import RobotCommand, validate_command


@dataclass(frozen=True)
class ROS2JointState:
    names: tuple[str, ...]
    positions: tuple[float, ...]
    velocities: tuple[float, ...] = ()

    def validate(self) -> None:
        if len(self.names) != len(self.positions):
            raise ValueError("joint names and positions must have equal length")
        if self.velocities and len(self.velocities) != len(self.names):
            raise ValueError("joint velocities must match joint names")
        if len(set(self.names)) != len(self.names):
            raise ValueError("joint names must be unique")
        if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in self.positions):
            raise ValueError("joint positions must be numeric")


@dataclass(frozen=True)
class ROS2Twist:
    linear_x: float = 0.0
    linear_y: float = 0.0
    angular_z: float = 0.0

    def as_tuple(self) -> tuple[float, float, float]:
        values = (self.linear_x, self.linear_y, self.angular_z)
        if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in values):
            raise ValueError("twist values must be numeric")
        return tuple(float(value) for value in values)


class ROS2Publisher(Protocol):
    def publish_joint_command(self, positions: tuple[float, ...]) -> None: ...
    def publish_base_command(self, velocity: tuple[float, float, float]) -> None: ...
    def publish_stop(self) -> None: ...


class DryRunROS2Publisher:
    """Capture ROS 2-style publications for integration tests."""

    def __init__(self) -> None:
        self.joint_commands: list[tuple[float, ...]] = []
        self.base_commands: list[tuple[float, float, float]] = []
        self.stop_count = 0

    def publish_joint_command(self, positions: tuple[float, ...]) -> None:
        self.joint_commands.append(tuple(positions))

    def publish_base_command(self, velocity: tuple[float, float, float]) -> None:
        self.base_commands.append(tuple(velocity))

    def publish_stop(self) -> None:
        self.stop_count += 1


class ROS2RobotBridge:
    """Translate validated TomatoAI commands into ROS 2-style publications."""

    def __init__(self, publisher: ROS2Publisher) -> None:
        self.publisher = publisher
        self.last_command: RobotCommand | None = None

    def send(self, command: RobotCommand) -> None:
        validate_command(command)
        self.publisher.publish_joint_command(command.joint_positions)
        self.publisher.publish_base_command(command.base_velocity)
        self.last_command = command

    def stop(self) -> None:
        self.publisher.publish_stop()


def joint_state_to_dict(state: ROS2JointState) -> dict[str, Any]:
    state.validate()
    return {
        "names": state.names,
        "positions": state.positions,
        "velocities": state.velocities,
    }
