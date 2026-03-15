from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Alice Smith"])
    email: EmailStr = Field(..., examples=["alice@example.com"])
    age: int = Field(..., ge=0, le=150, examples=[30])


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(default=None, ge=0, le=150)


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UsersListOut(BaseModel):
    total: int
    limit: int
    offset: int
    results: List[UserOut]
