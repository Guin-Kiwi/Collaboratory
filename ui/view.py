"""NiceGUI base view: presentation-layer skeleton for 3-tier architecture."""

from __future__ import annotations

from typing import Any
from nicegui import ui
from sqlalchemy.orm import Session

from database import db
from logic import task_manager, user_manager, permissions_manager, app_state
from database.models import User, Project, Task


class BaseView:
    """Abstract base class for all NiceGUI page/component views.

    Each concrete view represents one page or reusable UI widget.  It holds a
    reference to the service (logic layer) it needs and renders itself through
    :meth:`render`.

    Subclass this to build concrete views::

        class HomeView(BaseView):
            def render(self) -> None:
                ui.label("Welcome to the home page!")

    Args:
        service: Optional logic-layer service used by the view.
    """

    def __init__(self, service: Any = None) -> None:
        self._service = service
## check the actual nomanclature for the app_state _service calls
    def render(self) -> None:
        ui.label('CONTENT')
        [ui.label(f'Line {i}') for i in range(100)]
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            ui.button('Dashboard', on_click=lambda: ui.notify('Go to Dashboard')).props('flat color=white')
            ui.label(self._service.get_current_user().name).classes('text-bold')
            ui.label(self._service.get_current_user().task).classes('text-bold')
            ui.label(self._service.get_current_user().project).classes('text-bold')
            ui.button('Logout', on_click=lambda: ui.notify('Logged out!')).props('flat color=white')
            ## need to add I redirect to the login page here and also clear the app state of the user info on logout
            ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')
        with ui.left_drawer(top_corner=True, bottom_corner=True).style('background-color: #d7e3f4'):
            ui.label('Mentions')
            # add mentions list here with a mentions input box above
            ui.con
        with ui.right_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as right_drawer:
            ui.label('Project Overview').classes('text-bold')
            with ui.list().props('bordered separator'):
                ui.list_label('Assigned Users').props('header').classes('text-bold')
                for user in self._service.get_project_users():
                    username = user.username
                    name = user.name
                ui.separator()
                with ui.item(on_click=lambda: ui.notify('Selected contact 1')):
                    with ui.item_section().props('avatar'):
                        ui.icon('person')
                    with ui.item_section():
                        ui.item_label({username: str}).classes('text-bold')
                        ui.item_label({name: str}).props('caption')
                    with ui.item_section().props('side'):
                        ui.icon('mention')
        with ui.footer().style('background-color: #3874c8'):
            ui.label('FOOTER')
        with ui.page_sticky(position='bottom-left', x_offset=20, y_offset=20):
            ui.button('Sticky Button', on_click=lambda: ui.notify('Sticky Button Clicked'))
        with ui.page_scroller(position='bottom-right', x_offset=20, y_offset=20):
            ui.button('Scroll to Top')
        with ui.card().classes("w-full max-w-lg mx-auto mt-8"):
            ui.label(self.__class__.__name__).classes("text-2xl font-bold")
            ui.label(
                "Override BaseView.render() to build your page content here."
            ).classes("text-gray-500")
