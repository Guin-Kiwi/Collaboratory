# --- FOR UI DEVELOPERS ---
# To run the app locally:
#   python main.py
# Then open your browser at: http://localhost:8080
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


class LoginPage(BaseView):
    def render(self) -> None:
        public_frame()


@ui.page('/')
def login() -> None:
    LoginPage().render()
