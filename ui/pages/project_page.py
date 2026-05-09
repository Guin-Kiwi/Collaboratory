# --- FOR UI DEVELOPERS ---
# To run the app locally:
#   1. Run: python main.py
#   2. Log in at http://localhost:8080, then navigate to a project.
#
# This page inherits ProjectFrame from ui/layout.py.
# Override these action methods:
#
#   def on_create_task(self) -> None:
#       called when "Create Task" is clicked in the left drawer
#
#   def on_add_collaborator(self) -> None:
#       called when "Add Collaborator" is clicked in the right drawer
#       owner only — CollabManager will raise PermissionDenied if not allowed
#
#   def on_create_note(self) -> None:
#       called when "Create Note" is clicked in the body
#
# Data available in your methods:
#   self.user     — the logged-in User object
#   self.project  — the current Project object
#
# Useful manager calls (CollabManager from logic/collab_manager.py):
#   manager.view_collaborators(user, project_id)
#   manager.add_collaborator(user, project_id, user_id)
#   manager.remove_collaborator(user, project_id, user_id)
#   manager.create_project_note(user, project_id, content)
#   manager.edit_project_note(user, project_id, pnote_id, content)
#   manager.delete_project_note(user, project_id, pnote_id)


from nicegui import ui
from database import db_conn                # route function: fetch project
from database.models import Project         # route function: query type
from logic.app_state import app_state       # route function: get_current_user()
from logic.collab_manager import CollabManager   # on_create_note(), on_add_collaborator()
from logic.task_manager import TaskManager       # on_create_task()
from logic.user_manager import UserManager       # on_add_collaborator(): find user by username
from ui.layout import ProjectFrame

class ProjectPage(ProjectFrame):
    def on_create_task(self) -> None: ...
    def on_add_collaborator(self) -> None: ...
    def on_create_note(self) -> None: ...
    def on_create_task(self) -> None: ...    # "Create Task" button function, left drawer
    def on_add_collaborator(self) -> None: ...# "Add Collaborator" button function, right drawer
    def on_create_note(self) -> None: ...     # "Create Note" button function, body (via render_notes)


@ui.page('/project/{project_id}')

def project(project_id: int) -> None:

    session = db_conn.get_session()

    proj = session.query(Project).filter_by(id=project_id).first()

    ProjectPage(app_state.get_current_user(), proj).render()
