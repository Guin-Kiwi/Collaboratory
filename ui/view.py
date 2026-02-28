"""NiceGUI base view: presentation-layer skeleton for 3-tier architecture."""

from __future__ import annotations

from typing import Any

import nicegui.ui as ui


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
        """Render the NiceGUI components for this view.

        Override in concrete subclasses.  The default implementation shows a
        placeholder label so that the skeleton runs without errors.
        """
        with ui.card().classes("w-full max-w-lg mx-auto mt-8"):
            ui.label(self.__class__.__name__).classes("text-2xl font-bold")
            ui.label(
                "Override BaseView.render() to build your page content here."
            ).classes("text-gray-500")
