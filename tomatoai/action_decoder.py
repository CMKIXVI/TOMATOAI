"""Strict, provider-neutral decoding of VLA action outputs."""
from __future__ import annotations
from typing import Any

REQUIRED_VECTOR_FIELDS = ("joint_positions", "base_velocity")


def decode_vla_action(output: Any) -> dict[str, Any]:
    """Normalize common VLA output mappings before robot safety validation."""
    if not isinstance(output, dict):
        raise ValueError("VLA output must be a mapping")
    result = dict(output)
    for field in REQUIRED_VECTOR_FIELDS:
        if field in result:
            value = result[field]
            if not isinstance(value, (tuple, list)):
                raise ValueError(f"{field} must be a sequence")
            if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in value):
                raise ValueError(f"{field} must contain numeric values")
            result[field] = tuple(float(item) for item in value)
    if "gripper" in result and result["gripper"] is not None:
        if isinstance(result["gripper"], bool) or not isinstance(result["gripper"], (int, float)):
            raise ValueError("gripper must be numeric")
        result["gripper"] = float(result["gripper"])
    if "arm_extended" in result and not isinstance(result["arm_extended"], bool):
        raise ValueError("arm_extended must be boolean")
    return result
