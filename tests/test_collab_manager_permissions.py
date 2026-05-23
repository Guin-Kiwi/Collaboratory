import pytest
import uuid

from logic.collab_manager import CollabManager
from logic.permissions_manager import PermissionDenied
from database.models import User, Project, Task, Assignment
from database.collab_models import ProjectNote as PNote, TaskNote as TNote, ProjectMember as PMember


@pytest.fixture
def cm():
    from database.connection import DatabaseConnection
    from database.models import BaseModel
    conn = DatabaseConnection(db_path=":memory:")
    conn.init()
    session = conn.get_session()
    cm = CollabManager(session=session)
    yield cm
    session.close()
    BaseModel.metadata.drop_all(conn._engine)


def make_user(session, name, is_admin=False):
    suffix = uuid.uuid4().hex[:8]
    u = User(
        username=f"{name}_{suffix}",
        name=name,
        email=f"{name}_{suffix}@example.test",
        password="pass",
        is_admin=is_admin,
    )
    session.add(u)
    session.commit()
    return u


@pytest.fixture
def world(cm):
    """Shared actors and objects: admin, owner, collab, assignee, other, proj, task."""
    s = cm.session
    admin    = make_user(s, "admin", is_admin=True)
    owner    = make_user(s, "owner")
    collab   = make_user(s, "collab")
    assignee = make_user(s, "assignee")
    other    = make_user(s, "other")

    proj = Project(name="proj", owner_id=owner.id)
    s.add(proj)
    s.commit()

    s.add(PMember(project_id=proj.id, user_id=collab.id))
    s.commit()

    task = Task(title="task1", project_id=proj.id, created_by=owner.id)
    s.add(task)
    s.commit()

    s.add(Assignment(user_id=assignee.id, task_id=task.id))
    s.commit()

    return dict(
        admin=admin, owner=owner, collab=collab,
        assignee=assignee, other=other,
        proj=proj, task=task,
    )


# ---------------------------------------------------------------------------
# can_add_collaborator – admin and owner only
# ---------------------------------------------------------------------------

class TestCanAddCollaborator:
    def test_admin_and_owner_allowed(self, cm, world):
        assert cm.can_add_collaborator(world["admin"], world["proj"]) is True
        assert cm.can_add_collaborator(world["owner"], world["proj"]) is True

    def test_others_denied(self, cm, world):
        assert cm.can_add_collaborator(world["collab"],   world["proj"]) is False
        assert cm.can_add_collaborator(world["assignee"], world["proj"]) is False
        assert cm.can_add_collaborator(world["other"],    world["proj"]) is False

    def test_none_args_safe(self, cm, world):
        assert cm.can_add_collaborator(None, world["proj"]) is False
        assert cm.can_add_collaborator(world["owner"], None) is False


# ---------------------------------------------------------------------------
# can_delete_project_note – owner/admin only (collaborators use author bypass)
# ---------------------------------------------------------------------------

class TestCanDeleteProjectNote:
    def test_admin_and_owner_allowed(self, cm, world):
        assert cm.can_delete_project_note(world["admin"], world["proj"]) is True
        assert cm.can_delete_project_note(world["owner"], world["proj"]) is True

    def test_collaborator_not_allowed_by_permission_flag(self, cm, world):
        # Collaborators do not hold the broad DELETE_PROJECT_NOTE permission.
        # They can still delete their *own* notes via the author bypass in
        # delete_project_note(), but the permission flag itself must be False.
        assert cm.can_delete_project_note(world["collab"],   world["proj"]) is False
        assert cm.can_delete_project_note(world["assignee"], world["proj"]) is False
        assert cm.can_delete_project_note(world["other"],    world["proj"]) is False

    def test_none_args_safe(self, cm, world):
        assert cm.can_delete_project_note(None, world["proj"]) is False
        assert cm.can_delete_project_note(world["owner"], None) is False


# ---------------------------------------------------------------------------
# delete_project_note – author bypass and permission enforcement
# ---------------------------------------------------------------------------

class TestDeleteProjectNote:
    def _add_project_note(self, cm, world, author_key):
        note = PNote(content="note", project_id=world["proj"].id, created_by=world[author_key].id)
        cm.session.add(note)
        cm.session.commit()
        return note

    def test_owner_can_delete_any_note(self, cm, world):
        note = self._add_project_note(cm, world, "collab")
        assert cm.delete_project_note(world["owner"], world["proj"].id, note.id) is True

    def test_admin_can_delete_any_note(self, cm, world):
        note = self._add_project_note(cm, world, "collab")
        assert cm.delete_project_note(world["admin"], world["proj"].id, note.id) is True

    def test_author_bypass_lets_collaborator_delete_own_note(self, cm, world):
        note = self._add_project_note(cm, world, "collab")
        assert cm.delete_project_note(world["collab"], world["proj"].id, note.id) is True

    def test_collaborator_cannot_delete_others_note(self, cm, world):
        note = self._add_project_note(cm, world, "owner")
        with pytest.raises(PermissionDenied):
            cm.delete_project_note(world["collab"], world["proj"].id, note.id)

    def test_assignee_cannot_delete_any_project_note(self, cm, world):
        note = self._add_project_note(cm, world, "owner")
        with pytest.raises(PermissionDenied):
            cm.delete_project_note(world["assignee"], world["proj"].id, note.id)

    def test_outsider_cannot_delete_project_note(self, cm, world):
        note = self._add_project_note(cm, world, "owner")
        with pytest.raises(PermissionDenied):
            cm.delete_project_note(world["other"], world["proj"].id, note.id)


# ---------------------------------------------------------------------------
# create_task_note – assignees and admins only
# ---------------------------------------------------------------------------

class TestCreateTaskNote:
    def test_assignee_can_create(self, cm, world):
        assert cm.create_task_note(world["assignee"], world["task"].id, "note") is True

    def test_admin_can_create(self, cm, world):
        assert cm.create_task_note(world["admin"], world["task"].id, "note") is True

    def test_owner_cannot_create_unless_assigned(self, cm, world):
        # Owners do not automatically have WRITE_TASK_NOTE; they must be an assignee.
        with pytest.raises(PermissionDenied):
            cm.create_task_note(world["owner"], world["task"].id, "note")

    def test_collaborator_cannot_create(self, cm, world):
        with pytest.raises(PermissionDenied):
            cm.create_task_note(world["collab"], world["task"].id, "note")

    def test_outsider_cannot_create(self, cm, world):
        with pytest.raises(PermissionDenied):
            cm.create_task_note(world["other"], world["task"].id, "note")


# ---------------------------------------------------------------------------
# delete_task_note – author bypass, owner/admin can delete any
# ---------------------------------------------------------------------------

class TestDeleteTaskNote:
    def _add_task_note(self, cm, world, author_key):
        note = TNote(content="task note", task_id=world["task"].id, created_by=world[author_key].id)
        cm.session.add(note)
        cm.session.commit()
        return note

    def test_assignee_author_can_delete_own_note(self, cm, world):
        note = self._add_task_note(cm, world, "assignee")
        assert cm.delete_task_note(world["assignee"], world["task"].id, note.id) is True

    def test_owner_can_delete_assignees_note(self, cm, world):
        note = self._add_task_note(cm, world, "assignee")
        assert cm.delete_task_note(world["owner"], world["task"].id, note.id) is True

    def test_admin_can_delete_any_task_note(self, cm, world):
        note = self._add_task_note(cm, world, "assignee")
        assert cm.delete_task_note(world["admin"], world["task"].id, note.id) is True

    def test_collaborator_cannot_delete_others_task_note(self, cm, world):
        note = self._add_task_note(cm, world, "assignee")
        with pytest.raises(PermissionDenied):
            cm.delete_task_note(world["collab"], world["task"].id, note.id)

    def test_outsider_cannot_delete_task_note(self, cm, world):
        note = self._add_task_note(cm, world, "assignee")
        with pytest.raises(PermissionDenied):
            cm.delete_task_note(world["other"], world["task"].id, note.id)


# ---------------------------------------------------------------------------
# view_task_note – owner, collaborator, assignee, admin; not outsider
# ---------------------------------------------------------------------------

class TestViewTaskNote:
    def test_assignee_can_view(self, cm, world):
        assert isinstance(cm.view_task_note(world["assignee"], world["task"].id), list)

    def test_owner_can_view(self, cm, world):
        assert isinstance(cm.view_task_note(world["owner"], world["task"].id), list)

    def test_collaborator_can_view(self, cm, world):
        assert isinstance(cm.view_task_note(world["collab"], world["task"].id), list)

    def test_admin_can_view(self, cm, world):
        assert isinstance(cm.view_task_note(world["admin"], world["task"].id), list)

    def test_outsider_denied(self, cm, world):
        with pytest.raises(PermissionDenied):
            cm.view_task_note(world["other"], world["task"].id)
