"""create users table

Revision ID: 0001_create_users
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_create_users"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        # Soft-delete columns
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Primary key index (created implicitly, but explicit for clarity)
    op.create_index("ix_users_id", "users", ["id"])

    # Partial unique index on email for non-deleted rows
    op.create_index(
        "uix_users_email_not_deleted",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )

    # B-tree index on age for range queries / sorting
    op.create_index("ix_users_age", "users", ["age"])

    # Index on is_deleted for soft-delete filter performance
    op.create_index("ix_users_is_deleted", "users", ["is_deleted"])


def downgrade() -> None:
    op.drop_index("ix_users_is_deleted", table_name="users")
    op.drop_index("ix_users_age", table_name="users")
    op.drop_index("uix_users_email_not_deleted", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
