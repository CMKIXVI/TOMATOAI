"""Task outcome verification contracts."""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class VerificationRecord:
    task_id: str
    success: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    needs_review: bool = False
    reason: str | None = None

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id must not be empty")
        if not self.success and not self.reason:
            raise ValueError("failed tasks require a reason")
        if not isinstance(self.evidence, dict):
            raise ValueError("evidence must be a mapping")


def verify_task(
    task_id: str,
    success: bool,
    *,
    evidence: dict[str, Any] | None = None,
    needs_review: bool = False,
    reason: str | None = None,
) -> VerificationRecord:
    record = VerificationRecord(
        task_id=task_id,
        success=success,
        evidence=dict(evidence or {}),
        needs_review=needs_review,
        reason=reason,
    )
    record.validate()
    return record
