"""
User repository — all direct database access lives here.

Design decisions
----------------
- All queries filter ``is_deleted = false`` by default.
- ``delete()`` performs a soft delete (sets ``is_deleted`` and ``deleted_at``).
- The session is injected; transaction management is the caller's responsibility.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------ #
    # Read                                                                 #
    # ------------------------------------------------------------------ #

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return a non-deleted user by primary key, or None."""
        stmt = select(User).where(User.id == user_id, User.is_deleted.is_(False))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Return a non-deleted user by email (case-insensitive), or None."""
        stmt = select(User).where(
            func.lower(User.email) == email.lower(),
            User.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        include_inactive: bool = False,
    ) -> tuple[list[User], int]:
        """
        Return a paginated list of non-deleted users and the total count.

        Parameters
        ----------
        skip:
            Number of records to skip (offset).
        limit:
            Maximum number of records to return.
        include_inactive:
            When False (default) only active users are returned.
        """
        base = select(User).where(User.is_deleted.is_(False))
        if not include_inactive:
            base = base.where(User.is_active.is_(True))

        count_stmt = select(func.count()).select_from(base.subquery())
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        rows_stmt = base.order_by(User.created_at.desc()).offset(skip).limit(limit)
        rows = (await self._session.execute(rows_stmt)).scalars().all()

        return list(rows), total

    # ------------------------------------------------------------------ #
    # Write                                                                #
    # ------------------------------------------------------------------ #

    async def create(self, user: User) -> User:
        """Persist a new User instance and return it with DB-generated fields."""
        self._session.add(user)
        await self._session.flush()  # obtain DB-generated values without committing
        await self._session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Flush pending changes on an already-tracked User instance."""
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def delete(self, user: User) -> User:
        """
        Soft-delete a user by setting ``is_deleted = True`` and recording
        the deletion timestamp. The row is NOT removed from the database.
        """
        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False
        await self._session.flush()
        return user

    async def hard_delete(self, user: User) -> None:
        """
        Permanently remove a user row from the database.
        Use only for compliance / data-erasure requests.
        """
        await self._session.delete(user)
        await self._session.flush()
