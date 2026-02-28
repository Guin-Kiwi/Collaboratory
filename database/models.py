"""Declarative ORM base and a generic timestamped model mixin."""

from __future__ import annotations

import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    """Declarative base shared by all ORM model classes.

    Every concrete model should inherit from :class:`BaseModel` and define
    its own ``__tablename__`` and columns.  Common audit columns
    (``id``, ``created_at``, ``updated_at``) are provided via
    :class:`TimestampMixin`.

    Example::

        class Item(TimestampMixin, BaseModel):
            __tablename__ = "items"

            name: Mapped[str]
    """


class TimestampMixin:
    """Mixin that adds auto-managed *id*, *created_at*, and *updated_at* columns.

    Inherit from this mixin (before :class:`BaseModel`) on any concrete model
    that needs standard primary-key and audit-timestamp columns.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
