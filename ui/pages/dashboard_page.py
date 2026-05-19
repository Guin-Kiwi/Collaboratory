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
from logic.user_manager import UserManager
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

    def on_delete_account(self) -> None:
        um = UserManager(session=self.session)

        with ui.dialog().props('persistent') as dialog, ui.card().classes('w-[400px]'):
            ui.label("Delete Account").classes("text-h6 text-red")
            ui.label("This action is permanent and cannot be undone.").classes("text-sm text-grey")

            password_input = ui.input("Confirm your password", password=True) \
                .props('bordered') \
                .classes('w-full')

            error_label = ui.label("").classes("text-red text-sm")

            def confirm_delete():
                password = password_input.value.strip()
                if not password:
                    error_label.set_text("Please enter your password.")
                    return

                try:
                    ok = um.delete_account(self.user.id, password)
                    if ok:
                        app_state.logout()
                        dialog.close()
                        ui.navigate.to("/")
                    else:
                        error_label.set_text("Incorrect password.")
                except Exception as e:
                    error_label.set_text(f"Error: {str(e)}")

            with ui.row():
                ui.button("Delete My Account", on_click=confirm_delete).props('color=negative')
                ui.button("Cancel", on_click=dialog.close).props('flat')

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
