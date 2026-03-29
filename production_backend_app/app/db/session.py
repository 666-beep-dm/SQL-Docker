"""
Async SQLAlchemy 2.0 engine and session factory.
"""
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy import Uuid
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """
    Shared declarative base for all ORM models.

    type_annotation_map ensures that ``Mapped[uuid.UUID]`` columns are
    rendered as native PostgreSQL UUID columns (not VARCHAR) when using
    the asyncpg driver, which rejects Python uuid objects on VARCHAR cols.
    """

    type_annotation_map = {
        uuid.UUID: Uuid(as_uuid=True),
    }


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a transactional AsyncSession.
    The session is committed on success and rolled back on any exception.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
