from tomatoai.pipeline import PipelineInput, TomatoAIPipeline
from tomatoai.robot_bridge import DryRunRobotBridge
from tomatoai.temporal_state import TemporalState
from tomatoai.vla_adapter import VLAAdapter


class FakeEstimator:
    def update(self, observations):
        return TemporalState(
            timestamp=observations[-1].timestamp,
            growth_stage="fruiting",
            fruit_count=3,
            ripeness_distribution={"green": 2, "ripe": 1},
            stress_indicators={},
            confidence=0.9,
        )


class FakeVLA(VLAAdapter):
    def load(self, config):
        pass

    def prepare_observation(self, *, rgb, depth, robot_state, tomato_state, task):
        return {"tomato_state": tomato_state, "task": task}

    def propose_action(self, observation):
        return {"joint_positions": (0.1, 0.2), "gripper": 0.4}

    def decode_action(self, output):
        return dict(output)

    def metadata(self):
        return {"provider": "fake"}


def test_pipeline_connects_task_state_vla_and_robot():
    robot = DryRunRobotBridge()
    pipeline = TomatoAIPipeline(FakeEstimator(), FakeVLA(), robot)
    result = pipeline.run(
        PipelineInput(
            rgb="frame",
            depth=None,
            robot_state={},
            perception={"fruit_count": 3},
            environment={"air_temperature_c": 24.0},
            task={
                "task_id": "t-1",
                "task_type": "inspect",
                "approval_required": False,
            },
            timestamp="2026-10-22T08:00:00Z",
        )
    )
    assert result["task"].task_id == "t-1"
    assert result["state"]["fruit_count"] == 3
    assert robot.commands[-1] == result["command"]


def test_pipeline_verification_is_separate_from_execution():
    record = TomatoAIPipeline.verify(
        "t-1", True, evidence={"inspection_complete": True}
    )
    assert record.success
    assert record.evidence["inspection_complete"]
