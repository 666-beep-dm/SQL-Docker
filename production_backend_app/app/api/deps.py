"""
FastAPI dependency injection.

Usage
-----
In any router:

    from app.api.deps import get_user_service
    from app.services.user_service import UserService

    @router.get("/users")
    async def list_users(svc: UserService = Depends(get_user_service)):
        ...
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.user_service import UserService


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserService:
    """Provide a UserService with an injected AsyncSession."""
    return UserService(session)
