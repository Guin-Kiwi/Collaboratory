# --- FOR UI DEVELOPERS ---
# To run the app locally:
#   python main.py
# Then open your browser at: http://localhost:8080/dashboard
#
# This page will need data from CollabManager (logic/collab_manager.py).
# Create an instance with: manager = CollabManager()
#
# Useful calls for the dashboard:
#   manager.get_project_list_as_collaborator(user.id)
#       -> list of projects the logged-in user is a collaborator on (not their own projects)
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
#
# The logged-in user is always available via: app_state.get_current_user()
#
# FRAME:
#   This page uses dashboard_frame(page, user) from ui/layout.py.
#   Call it at the top of render() — it builds the header, left drawer (owned projects),
#   and right drawer (assigned tasks).
#   Add any extra ui elements after the call and they will appear in the main body area.
#   Example:
#       dashboard_frame(page="Dashboard", user=app_state.get_current_user())
#       ui.label("This appears in the main content area")
# -------------------------

from nicegui import ui

from ui.view import BaseView
from ui.layout import dashboard_frame
from logic.app_state import app_state
from database import db_conn
from database.models import User


class DashboardPage(BaseView):
    def render(self) -> None:
        dashboard_frame(page="Dashboard", user=app_state.get_current_user())


@ui.page('/dashboard')
def dashboard() -> None:
    # TODO: remove once login is wired up
    if not app_state.is_authenticated():
        session = db_conn.get_session()
        alice = session.query(User).filter_by(username="alice").first()
        app_state.login(alice)
    DashboardPage().render()
