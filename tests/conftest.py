import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from database.connection import DatabaseConnection
from database.models import BaseModel, User, Project, Task
from logic.user_manager import UserManager
from logic.project_manager import ProjectManager
from logic.task_manager import TaskManager


@pytest.fixture(scope="function")
def db():
    # ← use in-memory database so real tracker_app.db is never touched
    test_conn = DatabaseConnection(db_path=":memory:")
    test_conn.init()

    session = test_conn.get_session()

    yield session

    session.close()
    BaseModel.metadata.drop_all(test_conn._engine)


@pytest.fixture
def owner_user(db):
    user = User(
        username="owner",
        password="password",
        name="Owner User",
        email="owner@test.com",
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def normal_user(db):
    user = User(
        username="normal",
        password="password",
        name="Normal User",
        email="normal@test.com",
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def project(db, owner_user):
    project = Project(
        name="Test Project",
        description="Test project description",
        owner_id=owner_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def task(db, owner_user, project):
    task = Task(
        title="Test Task",
        description="Test task description",
        created_by=owner_user.id,
        project_id=project.id,
        due_date=None,
        priority="medium",
        status="todo",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task