from tomatoai.pipeline import PipelineInput, TomatoAIPipeline
from tomatoai.robot_bridge import DryRunRobotBridge
from tomatoai.temporal_state import TemporalState
from tomatoai.vla_adapter import VLAAdapter


class FakeEstimator:
    def update(self, observations):
        return TemporalState(
            timestamp=observations[-1].timestamp,
            growth_stage="flowering",
            fruit_count=3,
            ripeness_distribution={"green": 1.0},
            stress_indicators={},
            confidence=0.9,
        )


class FakeVLA(VLAAdapter):
    def load(self, config):
        self.config = config

    def prepare_observation(self, **kwargs):
        return kwargs

    def propose_action(self, observation):
        return {"joint_positions": (0.1, 0.2), "gripper": 0.5}

    def decode_action(self, output):
        return output

    def metadata(self):
        return {"provider": "fake"}


def test_pipeline_connects_state_vla_and_robot():
    robot = DryRunRobotBridge()
    pipeline = TomatoAIPipeline(FakeEstimator(), FakeVLA(), robot)
    result = pipeline.run(
        PipelineInput(
            rgb="frame",
            depth=None,
            robot_state={"ready": True},
            perception={"fruit_count": 3},
            environment={"temperature_c": 24.0},
            task={"name": "inspect"},
            timestamp="2026-10-22T00:00:00Z",
        )
    )
    assert result["state"]["fruit_count"] == 3
    assert result["action"]["gripper"] == 0.5
    assert len(robot.commands) == 1
