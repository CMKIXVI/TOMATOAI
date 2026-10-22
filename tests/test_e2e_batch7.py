import pytest

from tomatoai.pipeline import PipelineInput, TomatoAIPipeline
from tomatoai.robot_bridge import DryRunRobotBridge
from tomatoai.temporal_state import TemporalState
from tomatoai.vla_adapter import VLAAdapter


class E2EEstimator:
    def update(self, observations):
        latest = observations[-1]
        return TemporalState(
            timestamp=latest.timestamp,
            growth_stage=latest.perception.get("growth_stage", "fruiting"),
            fruit_count=int(latest.perception.get("fruit_count", 2)),
            ripeness_distribution=latest.perception.get("ripeness_distribution", {"green": 1.0}),
            stress_indicators=latest.perception.get("stress_indicators", {}),
            confidence=float(latest.perception.get("confidence", 0.9)),
        )


class E2EVLA(VLAAdapter):
    def load(self, config):
        self.config = config

    def prepare_observation(self, **kwargs):
        return kwargs

    def propose_action(self, observation):
        task_type = observation["task"]["task_type"]
        if task_type == "navigate":
            return {"base_velocity": (0.2, 0.0, 0.0)}
        if task_type == "manipulate":
            return {"joint_positions": (0.1, 0.2), "gripper": 0.5, "arm_extended": True}
        if task_type == "measure":
            return {"joint_positions": (0.05, 0.1), "gripper": 0.0}
        return {"joint_positions": (0.1, 0.2), "gripper": 0.5}

    def decode_action(self, output):
        return output

    def metadata(self):
        return {"provider": "e2e-test"}


def make_input(task_id, task_type, *, approval_required=False, approved=False, confidence=0.9):
    return PipelineInput(
        rgb="frame",
        depth="depth",
        robot_state={"ready": True},
        perception={
            "fruit_count": 2,
            "growth_stage": "fruiting",
            "ripeness_distribution": {"green": 0.75, "turning": 0.25},
            "stress_indicators": {},
            "confidence": confidence,
        },
        environment={"temperature_c": 24.0},
        task={
            "task_id": task_id,
            "task_type": task_type,
            "approval_required": approval_required,
            "approved": approved,
        },
        timestamp="2026-10-23T00:00:00Z",
    )


def run(task_id, task_type, **kwargs):
    robot = DryRunRobotBridge()
    pipeline = TomatoAIPipeline(E2EEstimator(), E2EVLA(), robot)
    result = pipeline.run(make_input(task_id, task_type, **kwargs))
    return result, robot


@pytest.mark.parametrize("task_type", ["inspect", "navigate", "measure", "manipulate"])
def test_all_task_types_complete_end_to_end(task_type):
    result, robot = run(f"e2e-{task_type}", task_type)
    assert not result["blocked"]
    assert result["verification"].success
    assert result["verification"].evidence["command_sent"] is True
    assert len(robot.commands) == 1


@pytest.mark.parametrize("index", range(120))
def test_repeated_e2e_runs_preserve_task_state_and_verification(index):
    task_type = ["inspect", "navigate", "measure", "manipulate"][index % 4]
    result, robot = run(f"batch7-{index}", task_type)
    assert result["task"].task_id == f"batch7-{index}"
    assert result["task"].task_type == task_type
    assert result["state"]["fruit_count"] == 2
    assert result["state"]["confidence"] == 0.9
    assert result["verification"].task_id == f"batch7-{index}"
    assert result["verification"].success
    assert len(robot.commands) == 1


@pytest.mark.parametrize("index", range(20))
def test_approval_gate_blocks_before_state_or_robot_execution(index):
    result, robot = run(
        f"approval-{index}",
        "manipulate",
        approval_required=True,
        approved=False,
    )
    assert result["blocked"]
    assert result["verification"].success is False
    assert result["verification"].needs_review
    assert result["verification"].reason
    assert len(robot.commands) == 0


@pytest.mark.parametrize("confidence", [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0])
def test_confidence_propagates_through_end_to_end_path(confidence):
    result, robot = run("confidence", "inspect", confidence=confidence)
    assert result["state"]["confidence"] == confidence
    assert result["verification"].evidence["state_confidence"] == confidence
    assert len(robot.commands) == 1


def test_explicit_approval_reaches_execution():
    result, robot = run("approved", "manipulate", approval_required=True, approved=True)
    assert not result["blocked"]
    assert result["verification"].success
    assert len(robot.commands) == 1


def test_pipeline_verify_records_failed_outcome_for_review():
    record = TomatoAIPipeline.verify(
        "post-run",
        False,
        evidence={"target_visible": False},
        needs_review=True,
        reason="target not visible",
    )
    assert not record.success
    assert record.needs_review
    assert record.evidence["target_visible"] is False


def test_navigation_command_does_not_extend_arm():
    result, robot = run("navigation", "navigate")
    assert result["command"].base_velocity == (0.2, 0.0, 0.0)
    assert not result["command"].arm_extended
    assert len(robot.commands) == 1


def test_manipulation_command_is_stationary_base():
    result, robot = run("manipulation", "manipulate")
    assert result["command"].arm_extended
    assert result["command"].base_velocity == (0.0, 0.0, 0.0)
    assert len(robot.commands) == 1


def test_e2e_output_contains_complete_execution_record():
    result, _ = run("record", "inspect")
    assert {"task", "blocked", "state", "action", "command", "verification"} <= result.keys()
    assert result["verification"].evidence["command_sent"] is True
