import pytest
import uuid

from logic.collab_manager import CollabManager
from database.models import User, Project, Task, Assignment
from database.collab_models import ProjectMember as PMember

@pytest.fixture
def cm():
    cm = CollabManager()
    # start a nested transaction so we can rollback after the test
    trans = cm.session.begin_nested()
    yield cm
    # rollback any changes made during test
    cm.session.rollback()
    cm.session.close()

def create_user(session, username, is_admin=False):
    suffix = uuid.uuid4().hex[:8]
    uname = f"{username}_{suffix}"
    u = User(
        username=uname,
        name=username,
        email=f'{uname}@example.test',
        password='pass',        # test-only dummy
        is_admin=is_admin,
    )
    session.add(u)
    session.commit()
    return u

def test_can_add_and_delete_permissions(cm):
    s = cm.session

    # create users
    admin = create_user(s, "admin", is_admin=True)
    owner = create_user(s, "owner", is_admin=False)
    collaborator = create_user(s, "collab", is_admin=False)
    assignee = create_user(s, "assignee", is_admin=False)
    other = create_user(s, "other", is_admin=False)

    # create project owned by `owner`
    proj = Project(name="p1", owner_id=owner.id)
    s.add(proj)
    s.commit()

    # add collaborator membership
    pm = PMember(project_id=proj.id, user_id=collaborator.id)
    s.add(pm)
    s.commit()

    # add a task and assign `assignee`
    task = Task(title="t1", project_id=proj.id, created_by=owner.id)
    s.add(task)
    s.commit()
    assignment = Assignment(user_id=assignee.id, task_id=task.id)
    s.add(assignment)
    s.commit()

    # can_add_collaborator: only admin and owner
    assert cm.can_add_collaborator(admin, proj) is True
    assert cm.can_add_collaborator(owner, proj) is True
    assert cm.can_add_collaborator(collaborator, proj) is False
    assert cm.can_add_collaborator(assignee, proj) is False
    assert cm.can_add_collaborator(other, proj) is False
    assert cm.can_add_collaborator(None, proj) is False
    assert cm.can_add_collaborator(owner, None) is False

    # can_delete_project_note: admin, owner, collaborator
    assert cm.can_delete_project_note(admin, proj) is True
    assert cm.can_delete_project_note(owner, proj) is True
    assert cm.can_delete_project_note(collaborator, proj) is True
    assert cm.can_delete_project_note(assignee, proj) is False
    assert cm.can_delete_project_note(other, proj) is False
    assert cm.can_delete_project_note(None, proj) is False
    assert cm.can_delete_project_note(owner, None) is False