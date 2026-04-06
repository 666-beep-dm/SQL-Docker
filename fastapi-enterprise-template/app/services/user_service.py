import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
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
            raise ConflictException(
                f"A user with email '{payload.email}' already exists."
            )
        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            age=payload.age,
        )
        created = await self.repo.create(user)
        logger.info(f"User created: {created.id} ({created.email})")
        return UserResponse.model_validate(created)

    async def get_user(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id '{user_id}' not found.")
        return UserResponse.model_validate(user)

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        include_inactive: bool = False,
    ) -> UserListResponse:
        users, total = await self.repo.get_all(
            skip=skip, limit=limit, include_inactive=include_inactive
        )
        return UserListResponse(
            total=total,
            items=[UserResponse.model_validate(u) for u in users],
        )

    async def update_user(
        self, user_id: uuid.UUID, payload: UserUpdate
    ) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id '{user_id}' not found.")

        if payload.email and payload.email != user.email:
            conflict = await self.repo.get_by_email(payload.email)
            if conflict:
                raise ConflictException(
                    f"Email '{payload.email}' is already taken."
                )
            user.email = payload.email

        if payload.first_name is not None:
            user.first_name = payload.first_name
        if payload.last_name is not None:
            user.last_name = payload.last_name
        if payload.age is not None:
            user.age = payload.age
        if payload.is_active is not None:
            user.is_active = payload.is_active
        if payload.password:
            user.hashed_password = hash_password(payload.password)

        updated = await self.repo.update(user)
        logger.info(f"User updated: {updated.id}")
        return UserResponse.model_validate(updated)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id '{user_id}' not found.")
        await self.repo.soft_delete(user)
        logger.info(f"User soft-deleted: {user_id}")
