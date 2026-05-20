import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from database.models import BaseModel, User, Project, Task, Assignment


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    BaseModel.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


def test_unique_constraint_prevents_duplicate_assignment(session):
    user = User(
        username="john_doe",
        name="John Doe",
        email="john@example.com",
        password="hashed_password",
        is_admin=False,
    )

    project = Project(
        name="Test Project",
        description="Testing project",
        owner=user,
    )

    task = Task(
        title="Test Task",
        description="Testing task",
        status="todo",
        priority="medium",
        project=project,
        creator=user,
    )

    session.add_all([user, project, task])
    session.commit()

    assignment_1 = Assignment(task_id=task.id, user_id=user.id)
    assignment_2 = Assignment(task_id=task.id, user_id=user.id)

    session.add(assignment_1)
    session.commit()

    session.add(assignment_2)

    with pytest.raises(IntegrityError):
        session.commit()
        