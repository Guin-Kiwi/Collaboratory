"""Application entry point: wires the three-tier architecture together.

Layers
------
database/   – SQLite connection and ORM model definitions  (data tier)
logic/      – Service classes for business logic            (logic tier)
ui/         – NiceGUI page/component views                  (presentation tier)

Run
---
    pip install -r requirements.txt
    python main.py
"""

from __future__ import annotations

import nicegui.ui as ui

from database import DatabaseConnection
from ui import BaseView


def main() -> None:
    """Initialise each layer and register NiceGUI routes."""

    # ── Data tier ──────────────────────────────────────────────────────────
    db = DatabaseConnection("app.db")
    db.init()

    # ── Logic tier ─────────────────────────────────────────────────────────
    # Services are instantiated per-request (inside route handlers) so that
    # each handler receives its own SQLAlchemy session.  Place shared,
    # stateless service configuration here if required.

    # ── Presentation tier ──────────────────────────────────────────────────
    @ui.page("/")
    def index() -> None:
        """Root page: renders the default placeholder view.

        When adding a feature, pass ``db.get_session()`` to the relevant
        service before constructing the view::

            session = db.get_session()
            service = SomeService(SomeModel, session)
            SomeView(service).render()
        """
        view = BaseView()
        view.render()

    # ── Start the NiceGUI server ────────────────────────────────────────────
    ui.run(title="Project Template")


if __name__ in {"__main__", "__mp_main__"}:
    main()
