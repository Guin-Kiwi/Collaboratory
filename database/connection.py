from __future__ import annotations
from pathlib import Path


from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from .models import BaseModel


class DatabaseConnection:
    """Manages the SQLAlchemy engine and session factory for a SQLite database.
    """

    def __init__(self, db_path:  str | None = None) -> None:
        
        
        """Initialise the connection with the path to the SQLite file.

        Args:
            db_path: Filesystem path for the SQLite database file.
                     Use ``":memory:"`` for an in-memory database.
        """
        if db_path is None:
            db_path = Path(__file__).resolve().parent / "tracker_app.db"
        self._db_url = f"sqlite:///{db_path}"
        self._engine: Engine | None = None
        self._session_factory: sessionmaker | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def init(self) -> None:
        """Create the engine, bind the session factory, and create all tables."""
        self._engine = create_engine(
            self._db_url,
            connect_args={"check_same_thread": False},
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
        )
        BaseModel.metadata.create_all(self._engine)

    def get_session(self) -> Session:
        """Return a new SQLAlchemy *Session* bound to this connection.

        The caller is responsible for committing and closing the session.
        For automatic lifecycle management use it as a context manager::

            with db.get_session() as session:
                ...

        Raises:
            RuntimeError: If :meth:`init` has not been called first.
        """
        if self._session_factory is None:
            raise RuntimeError(
                "DatabaseConnection has not been initialised. Call init() first."
            )
        return self._session_factory()

    def dispose(self) -> None:
        """Release all database connections held by the engine."""
        if self._engine is not None:
            self._engine.dispose()
