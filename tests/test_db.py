# tests/test_db.py
# Run with: pytest tests/test_db.py -v

import pytest
from sqlalchemy import select
from database.models import User, Project, Task, Assignment
from database.collab_models import ProjectMember, ProjectNote, TaskNote


# ---------------------------------------------------------------------------
# User tests
# ---------------------------------------------------------------------------

def test_create_user_persists_to_db(db):
    """Creating a user and committing saves it to the database."""
    user = User(
        username="testuser",
        password="hashed_password",
        name="Test User",
        email="test@test.com",
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    result = db.query(User).filter_by(username="testuser").first()
    assert result is not None
    assert result.username == "testuser"
    assert result.email == "test@test.com"
    assert result.is_admin is False


def test_user_username_is_unique(db):
    """Two users cannot share the same username."""
    from sqlalchemy.exc import IntegrityError

    user1 = User(username="duplicate", password="pass", name="User 1", email="user1@test.com")
    user2 = User(username="duplicate", password="pass", name="User 2", email="user2@test.com")

    db.add(user1)
    db.commit()

    db.add(user2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_user_email_is_unique(db):
    """Two users cannot share the same email."""
    from sqlalchemy.exc import IntegrityError

    user1 = User(username="user1", password="pass", name="User 1", email="same@test.com")
    user2 = User(username="user2", password="pass", name="User 2", email="same@test.com")

    db.add(user1)
    db.commit()

    db.add(user2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_admin_user_has_is_admin_true(db, owner_user):
    """Admin user fixture has is_admin set to True."""
    assert owner_user.is_admin is True


def test_normal_user_has_is_admin_false(db, normal_user):
    """Normal user fixture has is_admin set to False."""
    assert normal_user.is_admin is False


def test_delete_user_removes_from_db(db, owner_user):
    """Deleting a user removes them from the database."""
    db.delete(owner_user)
    db.commit()

    result = db.query(User).filter_by(id=owner_user.id).first()
    assert result is None


# ---------------------------------------------------------------------------
# Project tests
# ---------------------------------------------------------------------------

def test_create_project_persists_to_db(db, owner_user):
    """Creating a project and committing saves it to the database."""
    project = Project(
        name="My Project",
        description="A test project",
        owner_id=owner_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    result = db.query(Project).filter_by(name="My Project").first()
    assert result is not None
    assert result.description == "A test project"
    assert result.owner_id == owner_user.id


def test_project_owner_relationship(db, project, owner_user):
    """Project owner relationship resolves to the correct user."""
    db.refresh(project)
    assert project.owner_id == owner_user.id


def test_delete_project_removes_from_db(db, project):
    """Deleting a project removes it from the database."""
    project_id = project.id
    db.delete(project)
    db.commit()

    result = db.query(Project).filter_by(id=project_id).first()
    assert result is None


def test_delete_user_cascades_to_projects(db, owner_user, project):
    """Deleting a user also deletes their owned projects."""
    project_id = project.id
    db.delete(owner_user)
    db.commit()

    result = db.query(Project).filter_by(id=project_id).first()
    assert result is None


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_create_task_persists_to_db(db, owner_user, project):
    """Creating a task and committing saves it to the database."""
    task = Task(
        title="My Task",
        description="A test task",
        status="todo",
        priority="medium",
        created_by=owner_user.id,
        project_id=project.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    result = db.query(Task).filter_by(title="My Task").first()
    assert result is not None
    assert result.status == "todo"
    assert result.priority == "medium"
    assert result.project_id == project.id


def test_task_default_status_is_todo(db, task):
    """Task fixture has default status of todo."""
    assert task.status == "todo"


def test_task_default_priority_is_medium(db, task):
    """Task fixture has default priority of medium."""
    assert task.priority == "medium"


def test_update_task_status(db, task):
    """Updating a task status persists the change."""
    task.status = "in_progress"
    db.commit()
    db.refresh(task)

    assert task.status == "in_progress"


def test_delete_task_removes_from_db(db, task):
    """Deleting a task removes it from the database."""
    task_id = task.id
    db.delete(task)
    db.commit()

    result = db.query(Task).filter_by(id=task_id).first()
    assert result is None


def test_delete_project_cascades_to_tasks(db, project, task):
    """Deleting a project also deletes its tasks."""
    task_id = task.id
    db.delete(project)
    db.commit()

    result = db.query(Task).filter_by(id=task_id).first()
    assert result is None


# ---------------------------------------------------------------------------
# Assignment tests
# ---------------------------------------------------------------------------

def test_create_assignment_persists_to_db(db, owner_user, task):
    """Assigning a user to a task persists to the database."""
    assignment = Assignment(
        task_id=task.id,
        user_id=owner_user.id,
    )
    db.add(assignment)
    db.commit()

    result = db.query(Assignment).filter_by(
        task_id=task.id,
        user_id=owner_user.id,
    ).first()
    assert result is not None


def test_duplicate_assignment_raises_error(db, owner_user, task):
    """Assigning the same user to the same task twice raises an error."""
    from sqlalchemy.exc import IntegrityError

    assignment1 = Assignment(task_id=task.id, user_id=owner_user.id)
    assignment2 = Assignment(task_id=task.id, user_id=owner_user.id)

    db.add(assignment1)
    db.commit()

    db.add(assignment2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_delete_assignment_removes_from_db(db, owner_user, task):
    """Deleting an assignment removes it from the database."""
    assignment = Assignment(task_id=task.id, user_id=owner_user.id)
    db.add(assignment)
    db.commit()

    db.delete(assignment)
    db.commit()

    result = db.query(Assignment).filter_by(
        task_id=task.id,
        user_id=owner_user.id,
    ).first()
    assert result is None


def test_multiple_users_can_be_assigned_to_same_task(db, owner_user, normal_user, task):
    """Multiple different users can be assigned to the same task."""
    assignment1 = Assignment(task_id=task.id, user_id=owner_user.id)
    assignment2 = Assignment(task_id=task.id, user_id=normal_user.id)

    db.add(assignment1)
    db.add(assignment2)
    db.commit()

    results = db.query(Assignment).filter_by(task_id=task.id).all()
    assert len(results) == 2


# ---------------------------------------------------------------------------
# ProjectMember tests
# ---------------------------------------------------------------------------

def test_add_collaborator_persists_to_db(db, owner_user, normal_user, project):
    """Adding a collaborator to a project persists to the database."""
    member = ProjectMember(project_id=project.id, user_id=normal_user.id)
    db.add(member)
    db.commit()

    result = db.query(ProjectMember).filter_by(
        project_id=project.id,
        user_id=normal_user.id,
    ).first()
    assert result is not None


def test_duplicate_project_member_raises_error(db, owner_user, normal_user, project):
    """Adding the same collaborator twice raises an error."""
    from sqlalchemy.exc import IntegrityError

    member1 = ProjectMember(project_id=project.id, user_id=normal_user.id)
    member2 = ProjectMember(project_id=project.id, user_id=normal_user.id)

    db.add(member1)
    db.commit()

    db.add(member2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_remove_collaborator_removes_from_db(db, owner_user, normal_user, project):
    """Removing a collaborator deletes the membership from the database."""
    member = ProjectMember(project_id=project.id, user_id=normal_user.id)
    db.add(member)
    db.commit()

    db.delete(member)
    db.commit()

    result = db.query(ProjectMember).filter_by(
        project_id=project.id,
        user_id=normal_user.id,
    ).first()
    assert result is None


def test_multiple_collaborators_on_same_project(db, owner_user, normal_user, project):
    """Multiple users can collaborate on the same project."""
    user3 = User(username="user3", password="pass", name="User 3", email="user3@test.com")
    db.add(user3)
    db.commit()
    db.refresh(user3)

    member1 = ProjectMember(project_id=project.id, user_id=normal_user.id)
    member2 = ProjectMember(project_id=project.id, user_id=user3.id)
    db.add(member1)
    db.add(member2)
    db.commit()

    results = db.query(ProjectMember).filter_by(project_id=project.id).all()
    assert len(results) == 2


def test_delete_project_cascades_to_members(db, owner_user, normal_user, project):
    """Deleting a project also removes all its members."""
    member = ProjectMember(project_id=project.id, user_id=normal_user.id)
    db.add(member)
    db.commit()

    project_id = project.id
    db.delete(project)
    db.commit()

    result = db.query(ProjectMember).filter_by(project_id=project_id).first()
    assert result is None


# ---------------------------------------------------------------------------
# ProjectNote tests
# ---------------------------------------------------------------------------

def test_create_project_note_persists_to_db(db, owner_user, project):
    """Creating a project note persists to the database."""
    note = ProjectNote(
        content="This is a project note",
        project_id=project.id,
        created_by=owner_user.id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    result = db.query(ProjectNote).filter_by(project_id=project.id).first()
    assert result is not None
    assert result.content == "This is a project note"
    assert result.created_by == owner_user.id


def test_delete_project_note_removes_from_db(db, owner_user, project):
    """Deleting a project note removes it from the database."""
    note = ProjectNote(
        content="Note to delete",
        project_id=project.id,
        created_by=owner_user.id,
    )
    db.add(note)
    db.commit()

    note_id = note.id
    db.delete(note)
    db.commit()

    result = db.query(ProjectNote).filter_by(id=note_id).first()
    assert result is None


def test_update_project_note_content(db, owner_user, project):
    """Updating a project note content persists the change."""
    note = ProjectNote(
        content="Original content",
        project_id=project.id,
        created_by=owner_user.id,
    )
    db.add(note)
    db.commit()

    note.content = "Updated content"
    db.commit()
    db.refresh(note)

    assert note.content == "Updated content"


def test_delete_project_cascades_to_notes(db, owner_user, project):
    """Deleting a project also deletes its notes."""
    note = ProjectNote(
        content="Will be deleted",
        project_id=project.id,
        created_by=owner_user.id,
    )
    db.add(note)
    db.commit()

    note_id = note.id
    db.delete(project)
    db.commit()

    result = db.query(ProjectNote).filter_by(id=note_id).first()
    assert result is None


def test_multiple_notes_on_same_project(db, owner_user, project):
    """Multiple notes can be added to the same project."""
    note1 = ProjectNote(content="Note 1", project_id=project.id, created_by=owner_user.id)
    note2 = ProjectNote(content="Note 2", project_id=project.id, created_by=owner_user.id)
    db.add(note1)
    db.add(note2)
    db.commit()

    results = db.query(ProjectNote).filter_by(project_id=project.id).all()
    assert len(results) == 2


# ---------------------------------------------------------------------------
# TaskNote tests
# ---------------------------------------------------------------------------

def test_create_task_note_persists_to_db(db, owner_user, task):
    """Creating a task note persists to the database."""
    note = TaskNote(
        content="This is a task note",
        task_id=task.id,
        created_by=owner_user.id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    result = db.query(TaskNote).filter_by(task_id=task.id).first()
    assert result is not None
    assert result.content == "This is a task note"
    assert result.created_by == owner_user.id


def test_delete_task_note_removes_from_db(db, owner_user, task):
    """Deleting a task note removes it from the database."""
    note = TaskNote(
        content="Note to delete",
        task_id=task.id,
        created_by=owner_user.id,
    )
    db.add(note)
    db.commit()

    note_id = note.id
    db.delete(note)
    db.commit()

    result = db.query(TaskNote).filter_by(id=note_id).first()
    assert result is None


def test_update_task_note_content(db, owner_user, task):
    """Updating a task note content persists the change."""
    note = TaskNote(
        content="Original content",
        task_id=task.id,
        created_by=owner_user.id,
    )
    db.add(note)
    db.commit()

    note.content = "Updated content"
    db.commit()
    db.refresh(note)

    assert note.content == "Updated content"


def test_delete_task_cascades_to_notes(db, owner_user, task):
    """Deleting a task also deletes its notes."""
    note = TaskNote(
        content="Will be deleted",
        task_id=task.id,
        created_by=owner_user.id,
    )
    db.add(note)
    db.commit()

    note_id = note.id
    db.delete(task)
    db.commit()

    result = db.query(TaskNote).filter_by(id=note_id).first()
    assert result is None


def test_multiple_notes_on_same_task(db, owner_user, task):
    """Multiple notes can be added to the same task."""
    note1 = TaskNote(content="Note 1", task_id=task.id, created_by=owner_user.id)
    note2 = TaskNote(content="Note 2", task_id=task.id, created_by=owner_user.id)
    db.add(note1)
    db.add(note2)
    db.commit()

    results = db.query(TaskNote).filter_by(task_id=task.id).all()
    assert len(results) == 2