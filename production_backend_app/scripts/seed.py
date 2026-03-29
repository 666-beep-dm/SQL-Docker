"""
Seed script — populates the database with realistic test users.

Usage
-----
    # From the project root (with .env loaded or env vars set):
    python scripts/seed.py

The script is idempotent: it skips users whose email already exists.
"""
import asyncio
import sys
import os

# Ensure the project root is on sys.path when run directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.exc import IntegrityError

from app.core.logging import configure_logging, get_logger
from app.core.security import hash_password
from app.db.session import AsyncSessionFactory
from app.models.user import User

configure_logging()
logger = get_logger("seed")

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

SEED_USERS: list[dict] = [
    {
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice.johnson@example.com",
        "password": "Secure#Pass1",
        "age": 29,
    },
    {
        "first_name": "Bob",
        "last_name": "Smith",
        "email": "bob.smith@example.com",
        "password": "Secure#Pass2",
        "age": 34,
    },
    {
        "first_name": "Carol",
        "last_name": "Williams",
        "email": "carol.williams@example.com",
        "password": "Secure#Pass3",
        "age": 22,
    },
    {
        "first_name": "David",
        "last_name": "Brown",
        "email": "david.brown@example.com",
        "password": "Secure#Pass4",
        "age": 45,
    },
    {
        "first_name": "Eve",
        "last_name": "Davis",
        "email": "eve.davis@example.com",
        "password": "Secure#Pass5",
        "age": 31,
    },
    {
        "first_name": "Frank",
        "last_name": "Miller",
        "email": "frank.miller@example.com",
        "password": "Secure#Pass6",
        "age": None,  # age is optional
    },
    {
        "first_name": "Grace",
        "last_name": "Wilson",
        "email": "grace.wilson@example.com",
        "password": "Secure#Pass7",
        "age": 27,
    },
    {
        "first_name": "Henry",
        "last_name": "Moore",
        "email": "henry.moore@example.com",
        "password": "Secure#Pass8",
        "age": 52,
    },
    {
        "first_name": "Iris",
        "last_name": "Taylor",
        "email": "iris.taylor@example.com",
        "password": "Secure#Pass9",
        "age": 18,
    },
    {
        "first_name": "Jack",
        "last_name": "Anderson",
        "email": "jack.anderson@example.com",
        "password": "Secure#Pass10",
        "age": 60,
    },
]


async def seed() -> None:
    """Insert seed users, skipping any that already exist."""
    created = 0
    skipped = 0

    async with AsyncSessionFactory() as session:
        for data in SEED_USERS:
            user = User(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"].lower(),
                hashed_password=hash_password(data["password"]),
                age=data.get("age"),
            )
            session.add(user)
            try:
                await session.flush()
                created += 1
                logger.info("  ✔ Created user: %s", data["email"])
            except IntegrityError:
                await session.rollback()
                skipped += 1
                logger.info("  · Skipped (already exists): %s", data["email"])
                # Re-open the transaction for the next record
                async with session.begin_nested():
                    pass

        await session.commit()

    logger.info(
        "Seed complete — created: %d, skipped: %d, total: %d",
        created,
        skipped,
        len(SEED_USERS),
    )


if __name__ == "__main__":
    asyncio.run(seed())
