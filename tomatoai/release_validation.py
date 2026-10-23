"""Full-system release validation contracts for TomatoAI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True)
class ReleaseCheck:
    name: str
    passed: bool
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReleaseReport:
    checks: tuple[ReleaseCheck, ...]

    @property
    def count(self) -> int:
        return len(self.checks)

    @property
    def passed_count(self) -> int:
        return sum(check.passed for check in self.checks)

    @property
    def failed_count(self) -> int:
        return self.count - self.passed_count

    @property
    def passed(self) -> bool:
        return self.count > 0 and self.failed_count == 0

    def validate(self) -> None:
        if not self.checks:
            raise ValueError("release report requires at least one check")
        if any(not check.name for check in self.checks):
            raise ValueError("release check names must not be empty")


def build_release_report(checks: Iterable[ReleaseCheck]) -> ReleaseReport:
    report = ReleaseReport(tuple(checks))
    report.validate()
    return report
