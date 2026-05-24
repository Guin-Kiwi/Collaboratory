'''testing task logic'''

from database.models import Task


def test_task_status_change():
    task = Task(
        title="Test Task",
        description="Testing",
        priority="High",
        status="Open"
    )

    task.status = "Done"

    assert task.status == "Done"


def test_task_priority():
    task = Task(
        title="Test Task",
        description="Testing",
        priority="High",
        status="Open"
    )

    assert task.priority == "High"


def test_task_title():
    task = Task(
        title="My Task",
        description="Testing",
        priority="Low",
        status="Open"
    )

    assert task.title == "My Task"