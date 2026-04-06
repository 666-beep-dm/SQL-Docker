import asyncio
from logging.config import fileConfig
from urllib.parse import quote_plus

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.models.mixins import Base
from app.models.user import User  # noqa: F401 — ensures model is registered

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Build DATABASE_URL with safely encoded password."""
    password = quote_plus(settings.POSTGRES_PASSWORD)
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{password}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(get_url(), echo=False)
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn,
                target_metadata=target_metadata,
                compare_type=True,
            )
        )
        async with connection.begin():
            await connection.run_sync(lambda _: context.run_migrations())
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
