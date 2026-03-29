"""
User service layer.

Responsibilities
----------------
- Enforce business rules (duplicate email check, etc.).
- Orchestrate repository calls inside a single database transaction.
- Convert ORM models → response schemas when needed by callers.
- Hash passwords; never expose them.
"""
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate

logger = get_logger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = UserRepository(session)

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    async def _get_or_404(self, user_id: uuid.UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User", user_id)
        return user

    # ------------------------------------------------------------------ #
    # Commands                                                             #
    # ------------------------------------------------------------------ #

    async def create_user(self, payload: UserCreate) -> UserResponse:
        """
        Create a new user.

        Raises
        ------
        ConflictException
            If a non-deleted user with the same email already exists.
        """
        existing = await self._repo.get_by_email(payload.email)
        if existing is not None:
            raise ConflictException(
                f"A user with email '{payload.email}' already exists."
            )

        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email.lower().strip(),
            hashed_password=hash_password(payload.password),
            age=payload.age,
        )

        try:
            user = await self._repo.create(user)
        except IntegrityError as exc:
            logger.error("IntegrityError while creating user: %s", exc)
            raise ConflictException(
                f"A user with email '{payload.email}' already exists."
            ) from exc

        logger.info("Created user id=%s email=%s", user.id, user.email)
        return UserResponse.model_validate(user)

    async def update_user(
        self, user_id: uuid.UUID, payload: UserUpdate
    ) -> UserResponse:
        """
        Partially update an existing user.

        Only fields explicitly set in the payload are modified.

        Raises
        ------
        NotFoundException
            If no active user with ``user_id`` exists.
        """
        user = await self._get_or_404(user_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user = await self._repo.update(user)
        logger.info("Updated user id=%s fields=%s", user.id, list(update_data.keys()))
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """
        Soft-delete a user.

        Raises
        ------
        NotFoundException
            If no active user with ``user_id`` exists.
        """
        user = await self._get_or_404(user_id)
        await self._repo.delete(user)
        logger.info("Soft-deleted user id=%s", user_id)

    # ------------------------------------------------------------------ #
    # Queries                                                              #
    # ------------------------------------------------------------------ #

    async def get_user(self, user_id: uuid.UUID) -> UserResponse:
        """
        Retrieve a single user by ID.

        Raises
        ------
        NotFoundException
        """
        user = await self._get_or_404(user_id)
        return UserResponse.model_validate(user)

    async def list_users(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        include_inactive: bool = False,
    ) -> UserListResponse:
        """Return a paginated list of users."""
        users, total = await self._repo.list_users(
            skip=skip, limit=limit, include_inactive=include_inactive
        )
        return UserListResponse(
            total=total,
            items=[UserResponse.model_validate(u) for u in users],
        )
