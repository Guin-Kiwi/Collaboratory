"""Database layer: connection management and ORM model definitions."""

from pathlib import Path
from .connection import DatabaseConnection
from .models import BaseModel

# Shared instance — import this in your other modules
db = DatabaseConnection()
db.init()

__all__ = ["db", "DatabaseConnection", "BaseModel"]
