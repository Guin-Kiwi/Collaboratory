# --- FOR UI DEVELOPERS ---
# To run the app locally:
#   1. Run: python main.py
#   2. Open: http://localhost:8080
#   Log in first, then you will be redirected to /dashboard.
#
# This page inherits DashboardFrame from ui/layout.py.
# You do NOT call a frame function — instead override the action methods:
#
#   def on_create_project(self) -> None:
#       called when the user clicks "Create Project" in the left drawer
#       open a dialog here and call ProjectManager to save
#
# Data available in your methods:
#   self.user   — the logged-in User object
#
# Useful manager calls (CollabManager from logic/collab_manager.py):
#   manager.get_project_list_as_collaborator(user.id)
#   manager.view_collaborators(user, project_id)
#   manager.add_collaborator(user, project_id, user_id)
#   manager.remove_collaborator(user, project_id, user_id)
#   manager.create_project_note(user, project_id, content)
#   manager.edit_project_note(user, project_id, pnote_id, content)
#   manager.delete_project_note(user, project_id, pnote_id)

from nicegui import ui
from logic.app_state import app_state       # route function: get_current_user()
from logic.project_manager import ProjectManager  # on_create_project()
from ui.layout import DashboardFrame


class DashboardPage(DashboardFrame):
    def on_create_project(self) -> None:
        # open a dialog and call ProjectManager, remove pass when you implement this
        pass

@ui.page('/dashboard')
def dashboard() -> None:
    DashboardPage(app_state.get_current_user()).render()
