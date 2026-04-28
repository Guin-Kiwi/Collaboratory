"""NiceGUI base view: presentation-layer skeleton for 3-tier architecture."""

from __future__ import annotations

from typing import Any
from nicegui import ui
from sqlalchemy.orm import Session

#from database import db
from ui.layout import public_frame
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

    def render(self) -> None:
           public_frame()