from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_db
from app.schemas.user import UserCreate, UserOut, UserUpdate, UsersListOut

router = APIRouter(prefix="/users", tags=["users"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=UsersListOut, status_code=status.HTTP_200_OK)
async def list_users(
    db: DbDep,
    min_age: Optional[int] = Query(default=None, ge=0, le=150, description="Minimum age filter"),
    max_age: Optional[int] = Query(default=None, ge=0, le=150, description="Maximum age filter"),
    limit: int = Query(default=20, ge=1, le=100, description="Page size"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
    sort: Optional[str] = Query(
        default=None,
        description="Sort field. Prefix with '-' for DESC (e.g. 'name' or '-age')",
        examples={"asc": {"value": "name"}, "desc": {"value": "-age"}},
    ),
):
    if min_age is not None and max_age is not None and min_age > max_age:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_age must be less than or equal to max_age.",
        )

    total, users = await crud.get_users(
        db,
        min_age=min_age,
        max_age=max_age,
        limit=limit,
        offset=offset,
        sort=sort,
    )
    return UsersListOut(total=total, limit=limit, offset=offset, results=users)


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: DbDep):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found.")
    return user


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: DbDep):
    existing = await crud.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{payload.email}' is already registered.",
        )
    return await crud.create_user(db, payload)


@router.patch("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, payload: UserUpdate, db: DbDep):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found.")

    if payload.email and payload.email != user.email:
        existing = await crud.get_user_by_email(db, payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{payload.email}' is already registered.",
            )

    return await crud.update_user(db, user, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DbDep):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found.")
    await crud.delete_user(db, user)
