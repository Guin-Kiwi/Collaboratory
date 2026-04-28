from nicegui import ui

from ui.view import BaseView
from ui.layout import public_frame


class LoginPage(BaseView):
    def render(self) -> None:
        public_frame()


@ui.page('/')
def login() -> None:
    LoginPage().render()
