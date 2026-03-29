"""
User ORM model.
"""
from sqlalchemy import Boolean, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Application user.

    Indexes
    -------
    - Partial unique index on ``email`` where ``is_deleted = false``.
    - B-tree index on ``age`` for range / ORDER BY queries.
    - B-tree index on ``is_deleted`` (inherited from SoftDeleteMixin).
    """

    __tablename__ = "users"

    # ------------------------------------------------------------------ #
    # Columns                                                              #
    # ------------------------------------------------------------------ #
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ------------------------------------------------------------------ #
    # Table-level indexes / constraints                                    #
    # ------------------------------------------------------------------ #
    __table_args__ = (
        # Partial unique index: only one non-deleted account per email.
        Index(
            "uix_users_email_not_deleted",
            "email",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
        # Regular B-tree index on age.
        Index("ix_users_age", "age"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r}>"
