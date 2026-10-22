"""Deterministic temporal tomato-state estimator for development and evaluation."""
from __future__ import annotations

from collections import Counter
from typing import Sequence

from tomatoai.temporal_state import Observation, TemporalState


def estimate_temporal_state(observations: Sequence[Observation]) -> TemporalState:
    """Aggregate ordered observations without pretending to be a learned model."""
    if not observations:
        raise ValueError("at least one observation is required")
    timestamps = [item.timestamp for item in observations]
    if timestamps != sorted(timestamps):
        raise ValueError("observations must be ordered by timestamp")

    latest = observations[-1]
    fruit_counts = [o.perception.get("fruit_count") for o in observations]
    valid_counts = [
        int(v) for v in fruit_counts
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0
    ]
    fruit_count = valid_counts[-1] if valid_counts else None

    stages = [o.perception.get("growth_stage") for o in observations if o.perception.get("growth_stage")]
    growth_stage = Counter(stages).most_common(1)[0][0] if stages else None

    distribution = latest.perception.get("ripeness_distribution", {})
    ripeness = {str(k): float(v) for k, v in distribution.items() if float(v) >= 0}
    stress = {
        str(k): float(v)
        for k, v in latest.perception.get("stress_indicators", {}).items()
        if float(v) >= 0
    }
    completeness = sum(bool(o.perception) for o in observations) / len(observations)
    confidence = min(1.0, max(0.0, completeness))
    return TemporalState(
        timestamp=latest.timestamp,
        growth_stage=growth_stage,
        fruit_count=fruit_count,
        ripeness_distribution=ripeness,
        stress_indicators=stress,
        confidence=confidence,
    )
