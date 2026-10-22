import pytest

from tomatoai.robot_bridge import RobotCommand, validate_command


@pytest.mark.parametrize("gripper", [0.0, 0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0])
def test_valid_gripper_boundaries(gripper):
    validate_command(RobotCommand(gripper=gripper))


@pytest.mark.parametrize("gripper", [-1.0, -0.01, 1.01, 2.0])
def test_invalid_gripper_values_are_rejected(gripper):
    with pytest.raises(ValueError, match="gripper"):
        validate_command(RobotCommand(gripper=gripper))


@pytest.mark.parametrize("velocity", [(0.0, 0.0, 0.0), (0.1, 0.0, 0.0), (-0.1, 0.0, 0.0), (0.0, 0.1, 0.0), (0.0, -0.1, 0.0), (0.0, 0.0, 0.1), (0.0, 0.0, -0.1)])
def test_base_motion_allowed_with_retracted_arm(velocity):
    validate_command(RobotCommand(base_velocity=velocity, arm_extended=False))


@pytest.mark.parametrize("velocity", [
    (0.1, 0.0, 0.0), (-0.1, 0.0, 0.0), (0.0, 0.1, 0.0), (0.0, -0.1, 0.0),
    (0.0, 0.0, 0.1), (0.0, 0.0, -0.1), (1.0, 1.0, 0.0), (-1.0, 0.0, 1.0),
    (0.001, -0.002, 0.003),
])
def test_base_motion_is_blocked_with_extended_arm(velocity):
    with pytest.raises(ValueError, match="base motion"):
        validate_command(RobotCommand(base_velocity=velocity, arm_extended=True))


@pytest.mark.parametrize("joint_positions", [
    (), (0.0,), (0.1,), (-0.1,), (0.0, 0.0), (0.1, -0.2),
    (0.1, 0.2, 0.3), (-1.0, 0.0, 1.0), tuple(float(i) / 10 for i in range(10)),
])
def test_numeric_joint_positions_are_accepted(joint_positions):
    validate_command(RobotCommand(joint_positions=joint_positions))


@pytest.mark.parametrize("bad_joint", ["0.1", None, object(), True, False])
def test_non_numeric_joint_positions_are_rejected(bad_joint):
    with pytest.raises(ValueError, match="joint positions"):
        validate_command(RobotCommand(joint_positions=(bad_joint,)))


@pytest.mark.parametrize("index", range(70))
def test_repeated_safe_commands_remain_valid(index):
    command = RobotCommand(
        joint_positions=(index / 100.0, -index / 200.0),
        gripper=(index % 11) / 10.0,
        base_velocity=(0.0, 0.0, 0.0),
        arm_extended=index % 2 == 0,
    )
    validate_command(command)


@pytest.mark.parametrize("index", range(30))
def test_extended_arm_rejects_repeated_nonzero_base_motion(index):
    velocity = (0.01 + index / 1000.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="base motion"):
        validate_command(RobotCommand(base_velocity=velocity, arm_extended=True))
