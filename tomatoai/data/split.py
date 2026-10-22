"""Deterministic group-aware splitting helpers."""
from __future__ import annotations

from collections import defaultdict
import hashlib


def stable_group_split(group_id: str, ratios: dict[str, float]) -> str:
    """Assign a group to a split using a stable hash; groups never cross splits."""
    if not group_id:
        raise ValueError("group_id must not be empty")
    if not ratios or any(value < 0 for value in ratios.values()):
        raise ValueError("ratios must contain non-negative values")
    total = sum(ratios.values())
    if total <= 0:
        raise ValueError("ratios must have a positive total")
    bucket = int(hashlib.sha256(group_id.encode("utf-8")).hexdigest()[:12], 16) / 16**12
    cursor = 0.0
    for split, ratio in ratios.items():
        cursor += ratio / total
        if bucket < cursor:
            return split
    return next(reversed(ratios))


def assign_groups(group_ids: list[str], ratios: dict[str, float]) -> dict[str, str]:
    return {group_id: stable_group_split(group_id, ratios) for group_id in sorted(set(group_ids))}
