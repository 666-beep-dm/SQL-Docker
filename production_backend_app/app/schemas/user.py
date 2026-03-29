"""
Pydantic v2 schemas for the User resource.

Validation rules
----------------
- ``email`` is validated with Pydantic's built-in EmailStr type.
- ``age`` must be a positive integer when supplied.
- ``password`` is capped at 72 bytes (bcrypt's hard limit) measured in
  UTF-8 encoding, not character count, to prevent silent truncation.
- Passwords are write-only (never returned in response schemas).
"""
import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# --------------------------------------------------------------------------- #
# Shared / base                                                                #
# --------------------------------------------------------------------------- #


class UserBase(BaseModel):
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    email: EmailStr
    age: Annotated[int | None, Field(default=None, ge=0, le=150)]


# --------------------------------------------------------------------------- #
# Request schemas (inbound)                                                    #
# --------------------------------------------------------------------------- #


class UserCreate(UserBase):
    """Payload for POST /users."""

    # max_length=72 matches bcrypt's hard UTF-8 byte limit.
    # The validator below checks byte length, not character count,
    # so multi-byte characters (e.g. emoji) are still accounted for.
    password: Annotated[str, Field(min_length=8, max_length=72)]

    @field_validator("email")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        """Lowercase the email address for consistent storage."""
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def password_byte_length(cls, v: str) -> str:
        """
        Reject passwords whose UTF-8 encoding exceeds 72 bytes.

        bcrypt silently truncates at 72 bytes — enforcing this here turns
        a silent data-loss bug into a clear 422 validation error.
        """
        if len(v.encode("utf-8")) > 72:
            raise ValueError(
                "Password must not exceed 72 bytes when encoded as UTF-8. "
                "Passwords containing multi-byte characters (e.g. emoji) "
                "may be shorter in characters but longer in bytes."
            )
        return v


class UserUpdate(BaseModel):
    """
    Payload for PATCH /users/{id}.
    All fields are optional — only supplied fields are updated.
    """

    first_name: Annotated[str | None, Field(default=None, min_length=1, max_length=100)]
    last_name: Annotated[str | None, Field(default=None, min_length=1, max_length=100)]
    age: Annotated[int | None, Field(default=None, ge=0, le=150)]
    is_active: bool | None = None


# --------------------------------------------------------------------------- #
# Response schemas (outbound)                                                  #
# --------------------------------------------------------------------------- #


class UserResponse(UserBase):
    """Full user representation returned to API consumers."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Paginated list of users."""

    total: int
    items: list[UserResponse]