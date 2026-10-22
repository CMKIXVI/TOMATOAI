"""Provider-neutral robot execution boundary for TomatoAI."""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RobotCommand:
    joint_positions: tuple[float, ...] = ()
    gripper: float | None = None
    base_velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)
    arm_extended: bool = False


class RobotBridge(Protocol):
    def send(self, command: RobotCommand) -> None:
        ...

    def stop(self) -> None:
        ...


def validate_command(command: RobotCommand) -> None:
    """Reject commands that violate the default base/arm interlock."""
    if command.arm_extended and any(abs(value) > 0.0 for value in command.base_velocity):
        raise ValueError("base motion is forbidden while arm is extended")

    if command.gripper is not None and (
        isinstance(command.gripper, bool) or not 0.0 <= command.gripper <= 1.0
    ):
        raise ValueError("gripper must be in [0, 1]")

    if any(
        isinstance(value, bool) or not isinstance(value, (int, float))
        for value in command.joint_positions
    ):
        raise ValueError("joint positions must be numeric")

    if any(
        isinstance(value, bool) or not isinstance(value, (int, float))
        for value in command.base_velocity
    ):
        raise ValueError("base velocity must be numeric")


class DryRunRobotBridge:
    """Record validated commands without connecting to physical hardware."""

    def __init__(self) -> None:
        self.commands: list[RobotCommand] = []
        self.stopped = False

    def send(self, command: RobotCommand) -> None:
        validate_command(command)
        self.commands.append(command)
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True
