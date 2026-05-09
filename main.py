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
from nicegui import ui
import ui.pages

def main() -> None:
    """Initialise each layer and register NiceGUI routes."""

    # ── Data tier ──────────────────────────────────────────────────────────
    db = DatabaseConnection()
    db.init()

    # ── Start the NiceGUI server ────────────────────────────────────────────
    ui.run(title="Collaboratory", host="0.0.0.0")


if __name__ in {"__main__", "__mp_main__"}:
    main()
