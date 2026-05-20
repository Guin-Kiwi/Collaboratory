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
    """Login and registration page for unauthenticated users.

    Inherits from UnauthenticatedFrame which renders the header and
    login form shell. This class implements the login, signup, and
    forgot password logic.

    Attributes:
        _service: UserManager instance for all user-related database operations.
        _signup_dialog: Reference to the signup dialog, set during render_content().
        _forgot_dialog: Reference to the forgot password dialog, set during render_content().
    """

    def __init__(self):
        """Initialise the page with a UserManager service and empty dialog references."""
        self._service = UserManager()
        self._signup_dialog = None
        self._forgot_dialog = None

    def on_login(self, username: str, password: str, error_label) -> None:
        """Handle login form submission.

        Validates the credentials using UserManager. On success, logs the user
        in via AppState and redirects to the dashboard. On failure, displays
        an error message in the form.

        Args:
            username: The username entered in the login form.
            password: The password entered in the login form.
            error_label: The NiceGUI label element used to display error messages.
        """
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
        """Open the signup dialog if it has been initialised."""
        if self._signup_dialog:
            self._signup_dialog.open()

    def on_forgot_open(self) -> None:
        """Open the forgot password dialog if it has been initialised."""
        if self._forgot_dialog:
            self._forgot_dialog.open()

    def render_content(self) -> None:
        """Render the forgot password and signup dialogs.

        Called automatically by UnauthenticatedFrame.render() after the
        login form is built. Dialogs are created here and stored as instance
        attributes so on_signup_open() and on_forgot_open() can open them.
        """

        # --- forgot password dialog ---
        with ui.dialog() as forgot_dialog, ui.card().style('background-color: #d7e3f4').classes("items-center"):
            ui.label("Reset Password").classes("font-bold text-2xl text-center")

            forgot_username = ui.input("Username") \
                .props('bordered') \
                .classes('border border-solid border-gray-400 rounded') \
                .style("background-color: #FFFFFF")

            forgot_error = ui.label("").classes("text-red text-sm")
            forgot_success = ui.label("").classes("text-green text-sm")

            def handle_reset():
                """Validate the username and reset the password to a temporary one."""
                username = forgot_username.value.strip()
                if not username:
                    forgot_error.set_text("Please enter your username.")
                    forgot_success.set_text("")
                    return

                temp_password = self._service.reset_password(username)

                if temp_password:
                    forgot_error.set_text("")
                    forgot_success.set_text(f"Your temporary password is: {temp_password}")
                else:
                    forgot_success.set_text("")
                    forgot_error.set_text("Username not found.")

            with ui.row():
                ui.button("Reset Password", on_click=handle_reset)
                ui.button("Cancel", on_click=forgot_dialog.close).props('flat')

        self._forgot_dialog = forgot_dialog

        # --- signup dialog ---
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

            signup_error = ui.label("").classes("text-red text-sm")

            def handle_signup():
                """Validate signup fields and create a new standard user account.

                Checks for empty fields, valid email format, matching passwords,
                and username uniqueness before creating the user. On success,
                logs the user in and redirects to the dashboard.
                """
                try:
                    name = signup_name.value.strip()
                    email = signup_email.value.strip()
                    username = signup_username.value.strip()
                    password = signup_password.value.strip()
                    confirm = signup_confirm.value.strip()

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

                    user = self._service.create_user(username, password, name, email, is_admin=False)
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
    """Register the login page at the root route and render it."""
    LoginPage().render()