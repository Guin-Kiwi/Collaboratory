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

from logic.app_state import app_state
from logic.project_manager import ProjectManager
from ui.layout import DashboardFrame


class DashboardPage(DashboardFrame):

    def on_create_project(self) -> None:
        manager = ProjectManager(session=self.session)

        with ui.dialog() as dialog, ui.card():
            ui.label("Create Project").classes("text-2xl font-bold")

            name_input = ui.input("Project name").props("bordered").classes("w-full")
            description_input = ui.textarea("Description").props("bordered").classes("w-full")

            error_label = ui.label("").classes("text-red text-sm")

            def save_project() -> None:
                if not name_input.value:
                    error_label.text = "Project name is required."
                    return

                try:
                    manager.create_project(
                        user=self.user,
                        name=name_input.value,
                        description=description_input.value or "",
                        owner_id=self.user.id,
                    )

                    dialog.close()
                    ui.notify("Project created successfully.")
                    ui.navigate.to("/dashboard")

                except Exception as error:
                    error_label.text = str(error)

            with ui.row():
                ui.button("Cancel", on_click=dialog.close)
                ui.button("Create", on_click=save_project)

        dialog.open()


@ui.page('/dashboard')
def dashboard() -> None:
    user = app_state.get_current_user()

    if user is None:
        ui.navigate.to("/")
        return

    from logic.db_session import get_session 
    session = get_session()

    DashboardPage(user, session=session).render()
