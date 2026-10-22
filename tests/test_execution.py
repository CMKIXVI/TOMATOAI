import pytest

from tomatoai.robot_bridge import DryRunRobotBridge, RobotCommand, validate_command
from tomatoai.simulation import DryRunSimulator


def test_robot_interlock_blocks_base_motion_with_extended_arm():
    with pytest.raises(ValueError):
        validate_command(
            RobotCommand(base_velocity=(0.1, 0.0, 0.0), arm_extended=True)
        )


def test_dry_run_robot_records_valid_command():
    bridge = DryRunRobotBridge()
    command = RobotCommand(joint_positions=(0.1, 0.2), gripper=0.5)
    bridge.send(command)
    assert bridge.commands == [command]
    assert not bridge.stopped
    bridge.stop()
    assert bridge.stopped


def test_dry_run_simulator_progresses_and_closes():
    simulator = DryRunSimulator()
    assert simulator.reset()["status"] == "ready"
    result = simulator.step({"task": "inspect"})
    assert result["step"] == 1
    simulator.close()
    with pytest.raises(RuntimeError):
        simulator.step({"task": "inspect"})
