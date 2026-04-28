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
