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

from database.connection import DatabaseConnection
from logic import app_state
import ui.pages.login_page      # registers @ui.page('/')
import ui.pages.dashboard_page  # registers @ui.page('/dashboard')
import ui.pages.task_page       # registers @ui.page('/task/{task_id}')
import ui.pages.project_page   # registers @ui.page('/project/{project_id}')

from nicegui import ui


def main() -> None:
    """Initialise each layer and register NiceGUI routes."""

    # ── Data tier ──────────────────────────────────────────────────────────
    db = DatabaseConnection()
    db.init()

    # ── Start the NiceGUI server ────────────────────────────────────────────
    ui.run(title="Collaboratory")


if __name__ in {"__main__", "__mp_main__"}:
    main()
