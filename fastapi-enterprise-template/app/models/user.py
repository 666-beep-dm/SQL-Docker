from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixins import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, server_default="true"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
