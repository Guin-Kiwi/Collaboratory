# --- FOR UI DEVELOPERS ---
# To run the app locally:
# To view this page locally:
#   1. Run: python main.py
#   2. Open: http://localhost:8080/
#
# This page handles login. Authentication is managed through AppState (logic/app_state.py).
#
# Once you have verified the user's credentials, log them in with:
#   from logic.app_state import app_state
#   app_state.login(user)   <- pass the User object fetched from the database
#
# To check if someone is already logged in (e.g. redirect away from login):
#   app_state.is_authenticated()
#
# To log a user out:
#   app_state.logout()
#
# After login, redirect to /dashboard — that page expects app_state to have a current user set.
# See dashboard_page.py for what becomes available once the user is authenticated.
#
# FRAME:
#   This page uses UnauthenticatedFrame from ui/layout.py.
#   Implement on_login(), on_signup_open(), and render_content().
# -------------------------

# ui/login_page.py

from nicegui import ui

from ui.layout import UnauthenticatedFrame
from logic.app_state import app_state
from logic.user_manager import UserManager


class LoginPage(UnauthenticatedFrame):

    def __init__(self):
        self._service = UserManager()
        self._signup_dialog = None

    def on_login(self, username: str, password: str, error_label) -> None:
        if not username or not password:
            error_label.set_text("Please fill in both fields.")
            return

        user = self._service.validate_login(username.strip(), password.strip())

        if user:
            app_state.login(user)
            ui.navigate.to("/dashboard")
        else:
            error_label.set_text("Invalid username or password.")

    def on_signup_open(self) -> None:
        if self._signup_dialog:
            self._signup_dialog.open()

    def render_content(self) -> None:

        with ui.dialog() as signup_dialog, ui.card().style('background-color: #d7e3f4').classes("items-center"):
            ui.label("Create an Account").classes("font-bold text-2xl text-center")

            signup_name = ui.input("Full Name") \
                .props('bordered') \
                .classes('border border-solid border-gray-400 rounded') \
                .style("background-color: #FFFFFF")

            signup_email = ui.input("Email") \
                .props('bordered') \
                .classes('border border-solid border-gray-400 rounded') \
                .style("background-color: #FFFFFF")

            signup_username = ui.input("Username") \
                .props('bordered') \
                .classes('border border-solid border-gray-400 rounded') \
                .style("background-color: #FFFFFF")

            signup_password = ui.input("Password", password=True) \
                .props('bordered') \
                .classes('border border-solid border-gray-400 rounded') \
                .style("background-color: #FFFFFF")

            signup_confirm = ui.input("Confirm Password", password=True) \
                .props('bordered') \
                .classes('border border-solid border-gray-400 rounded') \
                .style("background-color: #FFFFFF")

            signup_is_admin = ui.checkbox("Register as Admin")

            signup_error = ui.label("").classes("text-red text-sm")

            def handle_signup():
                try:
                    name = signup_name.value.strip()
                    email = signup_email.value.strip()
                    username = signup_username.value.strip()
                    password = signup_password.value.strip()
                    confirm = signup_confirm.value.strip()
                    is_admin = signup_is_admin.value

                    if not name or not email or not username or not password or not confirm:
                        signup_error.set_text("Please fill in all fields.")
                        return

                    if "@" not in email or "." not in email:
                        signup_error.set_text("Please enter a valid email.")
                        return

                    if password != confirm:
                        signup_error.set_text("Passwords do not match.")
                        return

                    if self._service.user_exists(username):
                        signup_error.set_text("Username already taken.")
                        return

                    user = self._service.create_user(username, password, name, email, is_admin)
                    app_state.login(user)
                    signup_dialog.close()
                    ui.navigate.to("/dashboard")

                except Exception as e:
                    signup_error.set_text(f"Error: {str(e)}")

            with ui.row():
                ui.button("Create Account", on_click=handle_signup)
                ui.button("Cancel", on_click=signup_dialog.close).props('flat')

        self._signup_dialog = signup_dialog


@ui.page('/')
def login() -> None:
    LoginPage().render()