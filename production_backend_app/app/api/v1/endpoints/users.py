"""
User resource endpoints — full CRUD via the service layer.
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_user_service
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

# Convenience alias keeps signatures concise.
ServiceDep = Annotated[UserService, Depends(get_user_service)]


# --------------------------------------------------------------------------- #
# Create                                                                       #
# --------------------------------------------------------------------------- #


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(payload: UserCreate, svc: ServiceDep) -> UserResponse:
    """
    Register a new user.

    - **email**: Must be a valid, unique e-mail address.
    - **password**: Minimum 8 characters (stored as bcrypt hash).
    - **age**: Optional; must be between 0 and 150.
    """
    return await svc.create_user(payload)


# --------------------------------------------------------------------------- #
# Read                                                                         #
# --------------------------------------------------------------------------- #


@router.get(
    "",
    response_model=UserListResponse,
    summary="List users (paginated)",
)
async def list_users(
    svc: ServiceDep,
    skip: Annotated[int, Query(ge=0, description="Records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max records to return")] = 20,
    include_inactive: Annotated[
        bool, Query(description="Include inactive users")
    ] = False,
) -> UserListResponse:
    """
    Return a paginated list of non-deleted users.

    Soft-deleted users are never included regardless of ``include_inactive``.
    """
    return await svc.list_users(
        skip=skip, limit=limit, include_inactive=include_inactive
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a single user",
)
async def get_user(user_id: uuid.UUID, svc: ServiceDep) -> UserResponse:
    """Retrieve a user by their UUID primary key."""
    return await svc.get_user(user_id)


# --------------------------------------------------------------------------- #
# Update                                                                       #
# --------------------------------------------------------------------------- #


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Partially update a user",
)
async def update_user(
    user_id: uuid.UUID, payload: UserUpdate, svc: ServiceDep
) -> UserResponse:
    """
    Partially update a user's mutable fields.

    Only the fields present in the request body are modified;
    omitted fields are left unchanged.
    """
    return await svc.update_user(user_id, payload)


# --------------------------------------------------------------------------- #
# Delete                                                                       #
# --------------------------------------------------------------------------- #


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a user",
)
async def delete_user(user_id: uuid.UUID, svc: ServiceDep) -> None:
    """
    Soft-delete a user.

    The record is **not** physically removed from the database; the
    ``is_deleted`` flag is set to ``true`` and the user is deactivated.
    """
    await svc.delete_user(user_id)
