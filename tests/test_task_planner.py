import pytest

from tomatoai.task_planner import TaskRequest, make_task


def test_task_request_accepts_supported_task():
    task = make_task("t-1", "inspect", target={"plant_id": "p-1"})
    assert task.task_type == "inspect"
    assert task.approval_required


def test_task_request_rejects_unknown_task():
    with pytest.raises(ValueError):
        TaskRequest("t-1", "spray").validate()


def test_task_request_requires_id():
    with pytest.raises(ValueError):
        TaskRequest("", "inspect").validate()
