import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        include_inactive: bool = False,
    ) -> tuple[list[User], int]:
        query = select(User).where(User.is_deleted.is_(False))
        if not include_inactive:
            query = query.where(User.is_active.is_(True))

        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        result = await self.session.execute(
            query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def soft_delete(self, user: User) -> None:
        user.is_deleted = True
        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
