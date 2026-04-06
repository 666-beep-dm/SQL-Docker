import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_user_service
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.create_user(payload)


@router.get(
    "",
    response_model=UserListResponse,
    summary="List users (paginated)",
)
async def list_users(
    skip: int = Query(default=0, ge=0, description="Offset"),
    limit: int = Query(default=20, ge=1, le=100, description="Page size"),
    include_inactive: bool = Query(default=False, description="Include inactive users"),
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    return await service.list_users(skip=skip, limit=limit, include_inactive=include_inactive)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
)
async def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Partially update a user",
)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.update_user(user_id, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a user",
)
async def delete_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
) -> None:
    await service.delete_user(user_id)
