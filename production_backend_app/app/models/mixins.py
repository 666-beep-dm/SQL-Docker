"""
Reusable mixin that adds UUID primary key, audit timestamps,
and soft-delete support to any ORM model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column


def _utcnow() -> datetime:
    """Python-side UTC timestamp used as ORM-level default."""
    return datetime.now(timezone.utc)


class UUIDMixin:
    """
    Adds a UUID v4 primary key.

    Uses ``Uuid(as_uuid=True)`` so asyncpg sees a native UUID column,
    not a VARCHAR, avoiding driver-level type mismatch on INSERT/SELECT.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,   # Python-side: populated before flush
        index=True,
    )


class TimestampMixin:
    """
    Adds created_at / updated_at audit columns.

    Both ``default`` (Python-side) and ``server_default`` (DB-side) are
    set so the ORM object is always fully populated in memory immediately
    after flush, without needing a round-trip refresh from the DB.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,            # Python-side — available after flush
        server_default=func.now(),  # DB-side fallback for raw SQL inserts
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,            # Python-side — available after flush
        server_default=func.now(),  # DB-side fallback
        onupdate=_utcnow,           # Python-side on UPDATE
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Adds soft-delete support via an ``is_deleted`` boolean flag.

    Soft-deleted records remain in the database but are excluded
    from normal queries by the repository layer.
    """

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
