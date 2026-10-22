"""Minimal execution pipeline from observation to safe robot command."""
from dataclasses import dataclass
from typing import Any

from tomatoai.robot_bridge import RobotBridge, RobotCommand, validate_command
from tomatoai.safety import validate_confidence
from tomatoai.temporal_state import Observation, TemporalState, TemporalStateEstimator, validate_state
from tomatoai.vla_adapter import VLAAdapter


@dataclass(frozen=True)
class PipelineInput:
    rgb: Any
    depth: Any | None
    robot_state: dict[str, Any]
    perception: dict[str, Any]
    environment: dict[str, float]
    task: dict[str, Any]
    timestamp: str


class TomatoAIPipeline:
    """Orchestrate state estimation, VLA inference, safety, and execution."""

    def __init__(
        self,
        estimator: TemporalStateEstimator,
        vla: VLAAdapter,
        robot: RobotBridge,
    ) -> None:
        self.estimator = estimator
        self.vla = vla
        self.robot = robot

    def run(self, item: PipelineInput, history: list[Observation] | None = None) -> dict[str, Any]:
        observations = list(history or [])
        observations.append(
            Observation(
                timestamp=item.timestamp,
                perception=item.perception,
                environment=item.environment,
            )
        )
        state = self.estimator.update(observations)
        validate_state(state)
        if not validate_confidence(state.confidence):
            raise ValueError("invalid temporal-state confidence")

        tomato_state = {
            "timestamp": state.timestamp,
            "growth_stage": state.growth_stage,
            "fruit_count": state.fruit_count,
            "ripeness_distribution": state.ripeness_distribution,
            "stress_indicators": state.stress_indicators,
            "confidence": state.confidence,
        }
        observation = self.vla.prepare_observation(
            rgb=item.rgb,
            depth=item.depth,
            robot_state=item.robot_state,
            tomato_state=tomato_state,
            task=item.task,
        )
        output = self.vla.decode_action(self.vla.propose_action(observation))
        command = RobotCommand(
            joint_positions=tuple(output.get("joint_positions", ())),
            gripper=output.get("gripper"),
            base_velocity=tuple(output.get("base_velocity", (0.0, 0.0, 0.0))),
            arm_extended=bool(output.get("arm_extended", False)),
        )
        validate_command(command)
        self.robot.send(command)
        return {"state": tomato_state, "action": output, "command": command}
