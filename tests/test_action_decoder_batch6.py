import pytest
from tomatoai.action_decoder import decode_vla_action


@pytest.mark.parametrize("index", range(120))
def test_valid_vla_actions_decode_deterministically(index):
    output = {"joint_positions": [index / 100.0, -index / 200.0], "gripper": (index % 11) / 10.0, "arm_extended": index % 2 == 0}
    decoded = decode_vla_action(output)
    assert decoded["joint_positions"] == (index / 100.0, -index / 200.0)
    assert decoded["gripper"] == (index % 11) / 10.0
    assert decoded["arm_extended"] is (index % 2 == 0)


@pytest.mark.parametrize("field", ["joint_positions", "base_velocity"])
def test_vector_fields_require_sequences(field):
    with pytest.raises(ValueError, match="sequence"):
        decode_vla_action({field: "bad"})


@pytest.mark.parametrize("value", [[True], [False], ["1"], [None], [object()]])
def test_joint_vector_rejects_non_numeric_values(value):
    with pytest.raises(ValueError, match="numeric"):
        decode_vla_action({"joint_positions": value})


@pytest.mark.parametrize("value", [[True], [False], ["1"], [None], [object()]])
def test_base_vector_rejects_non_numeric_values(value):
    with pytest.raises(ValueError, match="numeric"):
        decode_vla_action({"base_velocity": value})


@pytest.mark.parametrize("value", [0, 0.0, 0.25, 0.5, 1, 1.0])
def test_gripper_numeric_values_decode_to_float(value):
    assert isinstance(decode_vla_action({"gripper": value})["gripper"], float)


@pytest.mark.parametrize("value", [True, False, "0.5", object(), []])
def test_gripper_rejects_non_numeric_values(value):
    with pytest.raises(ValueError, match="gripper"):
        decode_vla_action({"gripper": value})


@pytest.mark.parametrize("value", [True, False])
def test_arm_extended_accepts_boolean(value):
    assert decode_vla_action({"arm_extended": value})["arm_extended"] is value


@pytest.mark.parametrize("value", [0, 1, "true", None, [], {}])
def test_arm_extended_rejects_non_boolean(value):
    with pytest.raises(ValueError, match="boolean"):
        decode_vla_action({"arm_extended": value})


def test_non_mapping_output_is_rejected():
    with pytest.raises(ValueError, match="mapping"):
        decode_vla_action(None)


def test_unknown_fields_are_preserved():
    result = decode_vla_action({"confidence": 0.8, "mode": "inspect"})
    assert result == {"confidence": 0.8, "mode": "inspect"}


def test_none_gripper_is_preserved():
    assert decode_vla_action({"gripper": None})["gripper"] is None


def test_empty_action_is_valid_mapping():
    assert decode_vla_action({}) == {}
