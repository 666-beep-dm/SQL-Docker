import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def create_user(self, payload: UserCreate) -> UserResponse:
        existing = await self.repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{payload.email}' already exists.",
            )
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
        created = await self.repo.create(user)
        logger.info("User created", extra={"user_id": str(created.id)})
        return UserResponse.model_validate(created)

    async def get_user(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserResponse.model_validate(user)

    async def list_users(self, skip: int = 0, limit: int = 100) -> UserListResponse:
        users, total = await self.repo.get_all(skip=skip, limit=limit)
        return UserListResponse(
            total=total,
            items=[UserResponse.model_validate(u) for u in users],
        )

    async def update_user(self, user_id: uuid.UUID, payload: UserUpdate) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if payload.email and payload.email != user.email:
            conflict = await self.repo.get_by_email(payload.email)
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{payload.email}' is already taken.",
                )
            user.email = payload.email

        if payload.password:
            user.hashed_password = hash_password(payload.password)

        if payload.is_active is not None:
            user.is_active = payload.is_active

        updated = await self.repo.update(user)
        logger.info("User updated", extra={"user_id": str(updated.id)})
        return UserResponse.model_validate(updated)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        await self.repo.delete(user)
        logger.info("User deleted", extra={"user_id": str(user_id)})
