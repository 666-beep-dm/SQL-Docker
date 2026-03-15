from typing import Optional, Tuple

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

SORTABLE_COLUMNS = {"id", "name", "email", "age", "created_at", "updated_at"}


def _build_order_clause(sort: Optional[str]):
    if not sort:
        return asc(User.id)

    direction = desc if sort.startswith("-") else asc
    column_name = sort.lstrip("-")

    if column_name not in SORTABLE_COLUMNS:
        return asc(User.id)

    column = getattr(User, column_name)
    return direction(column)


async def get_users(
    db: AsyncSession,
    *,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    sort: Optional[str] = None,
) -> Tuple[int, list[User]]:
    base_query = select(User)

    if min_age is not None:
        base_query = base_query.where(User.age >= min_age)
    if max_age is not None:
        base_query = base_query.where(User.age <= max_age)

    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    order_clause = _build_order_clause(sort)
    data_query = base_query.order_by(order_clause).limit(limit).offset(offset)
    result = await db.execute(data_query)
    users = list(result.scalars().all())

    return total, users


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    user = User(**payload.model_dump())
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, payload: UserUpdate) -> User:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.flush()
