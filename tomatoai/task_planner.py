"""Typed, model-independent task planning contracts."""
from dataclasses import dataclass, field
from typing import Any


ALLOWED_TASKS = {"inspect", "navigate", "measure", "manipulate"}


@dataclass(frozen=True)
class TaskRequest:
    task_id: str
    task_type: str
    target: dict[str, Any] = field(default_factory=dict)
    approval_required: bool = True
    constraints: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id must not be empty")
        if self.task_type not in ALLOWED_TASKS:
            raise ValueError(f"unsupported task_type: {self.task_type}")
        if not isinstance(self.target, dict) or not isinstance(self.constraints, dict):
            raise ValueError("target and constraints must be mappings")


def make_task(task_id: str, task_type: str, **kwargs: Any) -> TaskRequest:
    task = TaskRequest(task_id=task_id, task_type=task_type, **kwargs)
    task.validate()
    return task
