"""
Idempotent seed script — inserts 10 test users.
Skips any user whose email already exists.

Usage:
    docker compose exec app python scripts/seed.py
    python scripts/seed.py   (locally)
"""
import asyncio
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User

SEED_USERS = [
    {"first_name": "Alice",   "last_name": "Johnson",   "email": "alice.johnson@example.com",   "age": 29},
    {"first_name": "Bob",     "last_name": "Smith",     "email": "bob.smith@example.com",       "age": 34},
    {"first_name": "Carol",   "last_name": "Williams",  "email": "carol.williams@example.com",  "age": 27},
    {"first_name": "David",   "last_name": "Brown",     "email": "david.brown@example.com",     "age": 45},
    {"first_name": "Eve",     "last_name": "Davis",     "email": "eve.davis@example.com",       "age": 31},
    {"first_name": "Frank",   "last_name": "Miller",    "email": "frank.miller@example.com",    "age": 38},
    {"first_name": "Grace",   "last_name": "Wilson",    "email": "grace.wilson@example.com",    "age": 26},
    {"first_name": "Henry",   "last_name": "Moore",     "email": "henry.moore@example.com",     "age": 52},
    {"first_name": "Iris",    "last_name": "Taylor",    "email": "iris.taylor@example.com",     "age": 23},
    {"first_name": "Jack",    "last_name": "Anderson",  "email": "jack.anderson@example.com",   "age": 41},
]

DEFAULT_PASSWORD = "Seed#Pass1"


async def seed() -> None:
    created = 0
    skipped = 0

    async with AsyncSessionLocal() as session:
        for data in SEED_USERS:
            result = await session.execute(
                select(User).where(User.email == data["email"], User.is_deleted.is_(False))
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"SKIP  Already exists: {data['email']}")
                skipped += 1
                continue

            user = User(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                hashed_password=hash_password(DEFAULT_PASSWORD),
                age=data["age"],
            )
            session.add(user)
            await session.flush()
            print(f"INFO  Created user: {data['email']}")
            created += 1

        await session.commit()

    total = created + skipped
    print(f"\nSeed complete — created: {created}, skipped: {skipped}, total: {total}")


if __name__ == "__main__":
    asyncio.run(seed())
