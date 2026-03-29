"""
Alembic environment script — async-aware.

Supports both ``--sql`` (offline) and online migration modes with
the async SQLAlchemy engine configured in ``app.db.session``.
"""
import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Ensure the app package is importable from inside the container (/app).
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import Base          # noqa: E402
from app.models import User              # noqa: E402, F401 — registers model with Base
from app.core.config import get_settings # noqa: E402

target_metadata = Base.metadata

_settings = get_settings()

# ---------------------------------------------------------------------------
# Migration helpers
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """
    Run migrations without a live DB connection (``--sql`` mode).
    Uses the sync psycopg2 URL so Alembic can render plain SQL.
    """
    context.configure(
        url=_settings.database_url_sync,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Build an asyncpg engine directly from Settings and run migrations.

    We use ``create_async_engine`` here instead of
    ``async_engine_from_config`` to guarantee the asyncpg driver is used
    regardless of what URL is written in alembic.ini.
    """
    connectable = create_async_engine(
        _settings.database_url,   # always postgresql+asyncpg://...
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
