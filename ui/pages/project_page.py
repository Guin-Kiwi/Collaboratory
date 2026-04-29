# --- FOR UI DEVELOPERS ---
# To view this page locally:
#   1. Run: python main.py
#   2. Open: http://localhost:8080
# Then open your browser at: http://localhost:8080/project/<id>
#
# This page will need data from CollabManager (logic/collab_manager.py).
# Create an instance with: manager = CollabManager()
#
# Useful calls for the project page:
#   manager.view_collaborators(user, project_id)
#       -> list of users who are collaborators on a given project
#   manager.add_collaborator(user, project_id, user_id)
#       -> adds a collaborator (owner only — will raise PermissionDenied if not allowed)
#   manager.remove_collaborator(user, project_id, user_id)
#       -> removes a collaborator (owner only)
#   manager.view_project_note(user, project_id)
#       -> list of notes on a project (owners and collaborators only)
#   manager.create_project_note(user, project_id, content)
#       -> add a note to a project (owners and collaborators only)
#   manager.edit_project_note(user, project_id, pnote_id, content)
#       -> only the original author of the note can edit it
#   manager.delete_project_note(user, project_id, pnote_id)
#       -> the note author, project owner, or admin can delete it
#
# The logged-in user is always available via: app_state.get_current_user()
#
# FRAME:
#   This page uses project_frame(page, user, project) from ui/layout.py.
#   Call it at the top of render() — it builds the header, left drawer (project tasks),
#   and right drawer (owned projects).
#   Add any extra ui elements after the call and they will appear in the main body area.
#   Example:
#       project_frame(page="Project", user=app_state.get_current_user(), project=proj)
#       ui.label("This appears in the main content area")
# -------------------------

from nicegui import ui

from ui.view import BaseView
from ui.layout import project_frame
from logic.app_state import app_state
from database import db_conn
from database.models import User, Project


class ProjectPage(BaseView):
    def render(self, proj: Project) -> None:
        project_frame(page="Project", user=app_state.get_current_user(), project=proj)


@ui.page('/project/{project_id}')
def project(project_id: int) -> None:
    session = db_conn.get_session()
    proj = session.query(Project).filter_by(id=project_id).first()

    # TODO: remove once login is wired up
    # DEV BYPASS: auto-logs in as alice (admin user) so you can view this page directly.
    # To test as a different user, comment out this block and go to http://localhost:8080 first.
    if not app_state.is_authenticated():
        alice = session.query(User).filter_by(username="alice").first()
        app_state.login(alice)
    ProjectPage().render(proj) #keep this though
