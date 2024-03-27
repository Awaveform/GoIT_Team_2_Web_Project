from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel, Field


class Roles(enum.Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class BaseUserModel(BaseModel):
    first_name: str
    last_name: str
    user_name: str


class UserModel(BaseUserModel):
    password: str


class UserResponse(BaseUserModel):
    id: int
    is_active: bool
    role: Roles
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True


class UserDetailedResponse(UserResponse):
    uploaded_photos: int


class UserRoleModel(BaseModel):
    user_id: int
    role_id: int
    created_at: datetime
    updated_at: datetime


class TokenModel(BaseModel):
    user_name: str = Field(min_length=5)
    password: str = Field(min_length=5)


class TokenModelResponse(BaseModel):
    access_token: str | None = Field(min_length=5)
    refresh_token: str | None = Field(min_length=5)
    token_type: str = "bearer"


class RateModel(BaseModel):
    grade: int


class RateModelResponse(RateModel):
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        orm_mode = True
