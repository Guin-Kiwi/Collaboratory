import datetime
from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

class TimestampMixin:
    """Mixin that adds auto-managed *id*, *created_at*, and *updated_at* columns.

    Inherit from this mixin (before :class:`BaseModel`) on any concrete model
    that needs standard primary-key and audit-timestamp columns.
    """

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