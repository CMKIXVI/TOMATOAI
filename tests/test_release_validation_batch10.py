"""Batch 10: 100+ full-system release validations."""
from datetime import datetime, timedelta, timezone

import pytest

from tomatoai.action_decoder import decode_vla_action
from tomatoai.benchmark import BenchmarkCase, run_classification_benchmark
from tomatoai.perception_baseline import BaselinePerception
from tomatoai.perception_state import predictions_to_plant_state
from tomatoai.release_validation import ReleaseCheck, build_release_report
from tomatoai.robot_bridge import RobotCommand, validate_command
from tomatoai.ros2_boundary import DryRunROS2Publisher, ROS2RobotBridge
from tomatoai.simulation import TomatoSimulation
from tomatoai.task_planner import make_task
from tomatoai.temporal_estimator import estimate_temporal_state
from tomatoai.temporal_state import Observation
from tomatoai.verification import verify_task


@pytest.mark.parametrize("case", range(120))
def test_full_system_release_path(case):
    """Exercise simulation -> perception -> state -> planning -> VLA -> robot -> ROS2 -> verification."""
    simulation = TomatoSimulation(plants=1 + case % 8, seed=case)
    initial = simulation.reset()
    sim_state = simulation.step({"temperature_c": 20.0 + case % 12, "irrigation": (case % 5) / 4.0})

    ripeness = ["green", "turning", "ripe"][case % 3]
    stage = ["vegetative", "flowering", "fruiting", "mature"][case % 4]
    perception = BaselinePerception().predict([
        {"label": ripeness, "confidence": 0.80 + (case % 5) * 0.04},
        {"label": stage, "confidence": 0.85},
    ])
    plant = predictions_to_plant_state(
        perception,
        observed_at=datetime(2026, 10, 22, tzinfo=timezone.utc) + timedelta(minutes=case),
        plant_id=f"plant-{case}",
        environment={"temperature_c": sim_state["temperature_c"]},
        provenance={"simulation_seed": case},
    )
    assert plant.fruit.visible_count == 1

    timestamp = (datetime(2026, 10, 22, tzinfo=timezone.utc) + timedelta(minutes=case)).isoformat()
    temporal = estimate_temporal_state([
        Observation(timestamp=timestamp, perception={
            "fruit_count": plant.fruit.visible_count,
            "growth_stage": plant.growth_stage,
            "ripeness_distribution": {ripeness: 1.0},
            "stress_indicators": {},
        }, environment={"temperature_c": sim_state["temperature_c"]})
    ])
    assert temporal.confidence == 1.0

    task_type = ["inspect", "navigate", "measure", "manipulate"][case % 4]
    task = make_task(f"release-{case}", task_type, target={"plant_id": plant.plant_id})
    assert task.task_type == task_type

    raw_action = {
        "joint_positions": [0.05 + case / 10000, 0.1, 0.15],
        "base_velocity": [0.0, 0.0, 0.0],
        "gripper": (case % 10) / 10.0,
        "arm_extended": True,
    }
    action = decode_vla_action(raw_action)
    command = RobotCommand(**action)
    validate_command(command)

    publisher = DryRunROS2Publisher()
    bridge = ROS2RobotBridge(publisher)
    bridge.send(command)
    assert publisher.joint_commands[-1] == command.joint_positions
    assert publisher.base_commands[-1] == command.base_velocity

    verification = verify_task(
        task.task_id,
        True,
        evidence={
            "simulation_step": sim_state["step"],
            "plant_id": plant.plant_id,
            "state_confidence": temporal.confidence,
            "ros2_published": True,
        },
    )
    assert verification.success

    benchmark = run_classification_benchmark(
        f"release-{case}",
        [BenchmarkCase("state", stage, stage)],
    )
    report = build_release_report([
        ReleaseCheck("simulation", initial["plants"] == simulation.plants),
        ReleaseCheck("perception", plant.fruit.visible_count == 1),
        ReleaseCheck("temporal_state", temporal.confidence == 1.0),
        ReleaseCheck("planning", task.task_id == f"release-{case}"),
        ReleaseCheck("action", command.arm_extended and command.gripper is not None),
        ReleaseCheck("ros2", len(publisher.joint_commands) == 1),
        ReleaseCheck("verification", verification.success),
        ReleaseCheck("benchmark", benchmark.passed),
    ])
    assert report.passed
    assert report.count == 8
    assert report.passed_count == 8


@pytest.mark.parametrize("case", range(20))
def test_release_safety_interlock_remains_blocking(case):
    command = RobotCommand(
        joint_positions=(0.1, 0.2),
        base_velocity=((case + 1) / 100.0, 0.0, 0.0),
        arm_extended=True,
    )
    with pytest.raises(ValueError, match="base motion"):
        validate_command(command)


@pytest.mark.parametrize("case", range(20))
def test_release_report_detects_failed_checks(case):
    report = build_release_report([
        ReleaseCheck("case", case % 2 == 0),
        ReleaseCheck("always", True),
    ])
    assert report.count == 2
    assert report.failed_count == (0 if case % 2 == 0 else 1)
    assert report.passed == (case % 2 == 0)


def test_release_report_rejects_empty_checks():
    with pytest.raises(ValueError):
        build_release_report([])
