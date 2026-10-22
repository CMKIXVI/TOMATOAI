"""Dependency-light TomatoAI execution smoke test."""
from tomatoai.pipeline import PipelineInput, TomatoAIPipeline
from tomatoai.robot_bridge import DryRunRobotBridge
from tomatoai.temporal_state import TemporalState
from tomatoai.vla_adapter import VLAAdapter


class SmokeEstimator:
    def update(self, observations):
        return TemporalState(
            timestamp=observations[-1].timestamp,
            growth_stage="vegetative",
            fruit_count=1,
            ripeness_distribution={"green": 1.0},
            stress_indicators={},
            confidence=1.0,
        )


class SmokeVLA(VLAAdapter):
    def load(self, config):
        self.config = config

    def prepare_observation(self, **kwargs):
        return kwargs

    def propose_action(self, observation):
        return {"joint_positions": (0.0,), "gripper": 0.0}

    def decode_action(self, output):
        return output

    def metadata(self):
        return {"provider": "smoke"}


def main() -> None:
    robot = DryRunRobotBridge()
    pipeline = TomatoAIPipeline(SmokeEstimator(), SmokeVLA(), robot)
    result = pipeline.run(
        PipelineInput(
            rgb="smoke-frame",
            depth=None,
            robot_state={"ready": True},
            perception={},
            environment={},
            task={"name": "inspect"},
            timestamp="2026-10-22T00:00:00Z",
        )
    )
    assert len(robot.commands) == 1
    print("TomatoAI pipeline smoke test passed")
    print(result["command"])


if __name__ == "__main__":
    main()
