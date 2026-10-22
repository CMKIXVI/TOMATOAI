import pytest

from tomatoai.robot_bridge import RobotCommand
from tomatoai.ros2_boundary import (
    DryRunROS2Publisher,
    ROS2JointState,
    ROS2RobotBridge,
    ROS2Twist,
    joint_state_to_dict,
)


@pytest.mark.parametrize("index", range(120))
def test_ros2_command_translation_is_deterministic(index):
    publisher = DryRunROS2Publisher()
    bridge = ROS2RobotBridge(publisher)
    command = RobotCommand(
        joint_positions=(index / 100.0, -index / 200.0),
        base_velocity=(0.1 if index % 2 else 0.0, 0.0, 0.01),
        gripper=0.5,
    )
    bridge.send(command)
    assert publisher.joint_commands[-1] == command.joint_positions
    assert publisher.base_commands[-1] == command.base_velocity
    assert bridge.last_command == command


@pytest.mark.parametrize("positions", [(), (0.0,), (0.1, -0.2), (1.0, 2.0, 3.0)])
def test_joint_state_round_trip(positions):
    names = tuple(f"joint_{i}" for i in range(len(positions)))
    state = ROS2JointState(names=names, positions=positions)
    result = joint_state_to_dict(state)
    assert result["names"] == names
    assert result["positions"] == positions


@pytest.mark.parametrize("count", range(20))
def test_joint_state_velocity_lengths(count):
    names = tuple(f"j{i}" for i in range(count))
    positions = tuple(float(i) for i in range(count))
    velocities = tuple(float(i) / 10 for i in range(count))
    ROS2JointState(names, positions, velocities).validate()


@pytest.mark.parametrize("values", [(0, 0, 0), (1, 2, 3), (-1, 0.5, -0.25), (0.0, 0.0, 1.0)])
def test_twist_normalizes_numeric_values(values):
    assert ROS2Twist(*values).as_tuple() == tuple(float(v) for v in values)


def test_bridge_stop_publishes_stop():
    publisher = DryRunROS2Publisher()
    ROS2RobotBridge(publisher).stop()
    assert publisher.stop_count == 1


def test_ros2_bridge_rejects_arm_base_conflict():
    publisher = DryRunROS2Publisher()
    bridge = ROS2RobotBridge(publisher)
    with pytest.raises(ValueError):
        bridge.send(RobotCommand(arm_extended=True, base_velocity=(0.1, 0.0, 0.0)))
    assert publisher.joint_commands == []
    assert publisher.base_commands == []


@pytest.mark.parametrize("bad", [("a",), (True,), (1, "bad"), (0.1, False)])
def test_joint_state_rejects_invalid_positions(bad):
    state = ROS2JointState(tuple(f"j{i}" for i in range(len(bad))), bad)
    with pytest.raises(ValueError):
        state.validate()


def test_joint_state_rejects_mismatched_names():
    with pytest.raises(ValueError):
        ROS2JointState(("j1",), (0.0, 1.0)).validate()


def test_joint_state_rejects_mismatched_velocities():
    with pytest.raises(ValueError):
        ROS2JointState(("j1", "j2"), (0.0, 1.0), (0.0,)).validate()


def test_joint_state_rejects_duplicate_names():
    with pytest.raises(ValueError):
        ROS2JointState(("j1", "j1"), (0.0, 1.0)).validate()


@pytest.mark.parametrize("value", ["x", True, None, object()])
def test_twist_rejects_non_numeric_values(value):
    with pytest.raises(ValueError):
        ROS2Twist(value, 0.0, 0.0).as_tuple()


def test_publisher_preserves_empty_joint_command():
    publisher = DryRunROS2Publisher()
    ROS2RobotBridge(publisher).send(RobotCommand())
    assert publisher.joint_commands == [()]
    assert publisher.base_commands == [(0.0, 0.0, 0.0)]


def test_stop_after_command_is_recorded():
    publisher = DryRunROS2Publisher()
    bridge = ROS2RobotBridge(publisher)
    bridge.send(RobotCommand(joint_positions=(0.1,)))
    bridge.stop()
    assert len(publisher.joint_commands) == 1
    assert publisher.stop_count == 1
