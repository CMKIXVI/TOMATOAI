"""Pure validation helpers for the high-level TomatoAI action boundary."""
from math import isfinite


def validate_confidence(value: float, threshold: float = 0.0) -> bool:
    return isfinite(value) and threshold <= value <= 1.0


def validate_scalar_limits(values: dict[str, float], limits: dict[str, tuple[float, float]]) -> bool:
    """Return True only when every supplied scalar is finite and inside its bound."""
    for key, value in values.items():
        if key not in limits or not isfinite(value):
            return False
        lower, upper = limits[key]
        if not lower <= value <= upper:
            return False
    return True
