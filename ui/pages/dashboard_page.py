from nicegui import ui, Client

from logic.app_state import app_state
from logic.project_manager import ProjectManager
from logic.user_manager import UserManager
from ui.layout import DashboardFrame


class DashboardPage(DashboardFrame):
    """Dashboard page for authenticated users.

    Inherits from DashboardFrame which renders the header, drawers,
    project lists, and task overview table. This class implements
    the create project and delete account actions.
    """

    def on_create_project(self) -> None:
        """Open a dialog to create a new project.

        Prompts the user for a project name and description.
        On confirmation, calls ProjectManager to persist the new
        project to the database and reloads the dashboard.
        """
        manager = ProjectManager(session=self.session)

        with ui.dialog() as dialog, ui.card():
            ui.label("Create Project").classes("text-2xl font-bold")

            name_input = ui.input("Project name").props("bordered").classes("w-full")
            description_input = ui.textarea("Description").props("bordered").classes("w-full")

            error_label = ui.label("").classes("text-red text-sm")

            def save_project() -> None:
                """Validate inputs and save the new project to the database."""
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
                    ui.notify("Project created successfully.", color='positive')
                    ui.navigate.to("/dashboard")

                except Exception as error:
                    error_label.text = str(error)

            with ui.row():
                ui.button("Cancel", on_click=dialog.close)
                ui.button("Create", on_click=save_project)

        dialog.open()

    def on_delete_account(self) -> None:
        """Open a dialog to permanently delete the current user's account.

        Requires the user to confirm their password before deletion.
        On success, logs the user out and redirects to the login page.
        The action is irreversible.
        """
        um = UserManager(session=self.session)

        with ui.dialog().props('persistent') as dialog, ui.card().classes('w-[400px]'):
            ui.label("Delete Account").classes("text-h6 text-red")
            ui.label("This action is permanent and cannot be undone.").classes("text-sm text-grey")

            password_input = ui.input("Confirm your password", password=True) \
                .props('bordered') \
                .classes('w-full')

            error_label = ui.label("").classes("text-red text-sm")

            def confirm_delete():
                """Verify the password and delete the account if correct."""
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
async def dashboard(client: Client) -> None:
    """Register the dashboard page at /dashboard and render it.

    Redirects to the login page if no user is currently authenticated.
    Passes the current user and an active database session to DashboardPage.
    The session is closed when the client disconnects.
    """
    user = app_state.get_current_user()

    if user is None:
        ui.navigate.to("/")
        return

    from logic.db_session import get_session
    session = get_session()
    try:
        DashboardPage(user, session=session).render()
        await client.disconnected()
    finally:
        session.close()