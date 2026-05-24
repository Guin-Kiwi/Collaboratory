from datetime import datetime

import pytest

from database.models import Assignment
from logic.task_manager import TaskManager
from logic.permissions_manager import PermissionDenied


def test_owner_can_create_task(db, owner_user, project):
    tm = TaskManager(session=db)

    task = tm.create_task(
        user=owner_user,
        project=project,
        title="Test task",
        description="Test description",
        due_date=None,
        priority="medium",
        status="todo",
    )

    assert task.id is not None
    assert task.title == "Test task"
    assert task.status == "todo"


def test_owner_can_assign_user_to_task(db, owner_user, normal_user, project, task):
    tm = TaskManager(session=db)

    ok = tm.assign_task(
        user=owner_user,
        project=project,
        task_id=task.id,
        assigned_user_id=normal_user.id,
    )

    assert ok is True

    assignees = tm.get_assignees(owner_user, task.id)

    assert len(assignees) == 1
    assert assignees[0].id == normal_user.id


def test_assignee_can_change_task_status(db, owner_user, normal_user, project, task):
    tm = TaskManager(session=db)

    tm.assign_task(
        user=owner_user,
        project=project,
        task_id=task.id,
        assigned_user_id=normal_user.id,
    )

    ok = tm.change_task_status(
        user=normal_user,
        project=project,
        task_id=task.id,
        status="completed",
    )

    assert ok is True
    assert task.status == "completed"


def test_remove_assignee_removes_user_from_task(db, owner_user, normal_user, project, task):
    tm = TaskManager(session=db)

    tm.assign_task(
        user=owner_user,
        project=project,
        task_id=task.id,
        assigned_user_id=normal_user.id,
    )

    ok = tm.remove_assignee(
        user=owner_user,
        task_id=task.id,
        assigned_user_id=normal_user.id,
    )

    assert ok is True

    assignees = tm.get_assignees(owner_user, task.id)

    assert len(assignees) == 0


def test_completed_task_status_is_saved(db, owner_user, normal_user, project, task):
    tm = TaskManager(session=db)

    tm.assign_task(
        user=owner_user,
        project=project,
        task_id=task.id,
        assigned_user_id=normal_user.id,
    )

    tm.change_task_status(
        user=normal_user,
        project=project,
        task_id=task.id,
        status="completed",
    )

    db.refresh(task)

    assert task.status == "completed"