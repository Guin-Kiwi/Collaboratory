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
#   This page uses public_frame() from ui/layout.py.
#   Call it at the top of render() — it builds the header and login card shell.
#   Add any extra ui elements after the call and they will appear in the main body.
# -------------------------

from nicegui import ui

from ui.view import BaseView
from ui.layout import public_frame
from logic.app_state import app_state
from logic.user_manager import UserManager


class LoginPage(BaseView):

    def __init__(self):
        super().__init__(service=UserManager())

    def render(self) -> None:
        public_frame()

        error_label = ui.label("").classes("text-red text-sm")

        def handle_login():
            username = username_input.value.strip()
            password = password_input.value.strip()

            if not username or not password:
                error_label.set_text("Please fill in both fields.")
                return

            user = self._service.validate_login(username, password)

            if user:
                app_state.login(user)
                ui.navigate.to("/dashboard")
            else:
                error_label.set_text("Invalid username or password.")

        username_input = ui.input("Username") \
            .props('bordered') \
            .classes('border border-solid border-gray-400 rounded') \
            .style("background-color: #FFFFFF")

        password_input = ui.input("Password", password=True) \
            .props('bordered') \
            .classes('border border-solid border-gray-400 rounded') \
            .style("background-color: #FFFFFF")

        ui.button("Login", on_click=handle_login)
        error_label


@ui.page('/')
def login() -> None:
    LoginPage().render()
