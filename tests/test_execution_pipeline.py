import pytest

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


def make_input(**task):
    return PipelineInput(
        rgb="frame",
        depth=None,
        robot_state={"ready": True},
        perception={"fruit_count": 3},
        environment={"temperature_c": 24.0},
        task=task,
        timestamp="2026-10-22T00:00:00Z",
    )


def test_pipeline_connects_state_vla_and_robot():
    robot = DryRunRobotBridge()
    pipeline = TomatoAIPipeline(FakeEstimator(), FakeVLA(), robot)
    result = pipeline.run(make_input(task_id="t-1", task_type="inspect", approval_required=False))
    assert result["state"]["fruit_count"] == 3
    assert result["action"]["gripper"] == 0.5
    assert len(robot.commands) == 1
    assert result["verification"].success
    assert not result["blocked"]


def test_pipeline_blocks_unapproved_task_without_robot_command():
    robot = DryRunRobotBridge()
    pipeline = TomatoAIPipeline(FakeEstimator(), FakeVLA(), robot)
    result = pipeline.run(make_input(task_id="t-2", task_type="inspect", approval_required=True))
    assert result["blocked"]
    assert result["verification"].needs_review
    assert len(robot.commands) == 0


def test_pipeline_executes_explicitly_approved_task():
    robot = DryRunRobotBridge()
    pipeline = TomatoAIPipeline(FakeEstimator(), FakeVLA(), robot)
    result = pipeline.run(
        make_input(task_id="t-3", task_type="inspect", approval_required=True, approved=True)
    )
    assert not result["blocked"]
    assert result["verification"].success
    assert len(robot.commands) == 1


@pytest.mark.parametrize("task_type", ["inspect", "navigate", "measure", "manipulate"])
def test_all_supported_task_types_reach_execution(task_type):
    robot = DryRunRobotBridge()
    pipeline = TomatoAIPipeline(FakeEstimator(), FakeVLA(), robot)
    result = pipeline.run(
        make_input(task_id=f"{task_type}-1", task_type=task_type, approval_required=False)
    )
    assert result["task"].task_type == task_type
    assert len(robot.commands) == 1


@pytest.mark.parametrize("index", range(100))
def test_pipeline_repeated_dry_runs_are_deterministic(index):
    robot = DryRunRobotBridge()
    pipeline = TomatoAIPipeline(FakeEstimator(), FakeVLA(), robot)
    result = pipeline.run(
        make_input(task_id=f"inspect-{index}", task_type="inspect", approval_required=False)
    )
    assert result["state"]["confidence"] == 0.9
    assert result["action"]["joint_positions"] == (0.1, 0.2)
    assert result["command"].gripper == 0.5
    assert result["verification"].evidence["command_sent"] is True
