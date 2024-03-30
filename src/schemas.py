from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, PositiveInt

from src.enums import Roles


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
    user_name: str = Field(min_length=4)
    password: str = Field(min_length=4)


class TokenModelResponse(BaseModel):
    access_token: str | None = Field(min_length=5)
    refresh_token: str | None = Field(min_length=5)
    token_type: str = "bearer"


class PhotoBase(BaseModel):
    description: str | None = Field(max_length=500)


class PhotoResponse(PhotoBase):
    id: int
    url: str
    created_by: int
    created_at: datetime


class PhotoBase(BaseModel):
    description: str | None = Field(max_length=500)


class PhotoResponse(PhotoBase):
    id: int
    url: str
    created_by: int
    created_at: datetime


class BaseTransformParamsModel(BaseModel):
    effect: str | None
    angle: PositiveInt | None
    crop: str | None
    gravity: str | None
    width: PositiveInt | None
    height: PositiveInt | None


class TransformPhotoModel(BaseModel):
    to_override: bool
    description: str
    params: BaseTransformParamsModel


class TransformedPhotoModelResponse(BaseModel):
    id: int
    url: str
    description: str
    created_at: datetime
    updated_at: datetime | None
    created_by: int
    updated_by: int | None
    original_photo_id: int | None
    is_transformed: bool | None

    class Config:
        orm_mode = True


class RateModel(BaseModel):
    grade: int = Field(ge=1, le=5)


class RateModelResponse(RateModel):
    created_at: datetime
    updated_at: datetime | None
    created_by: int

    class Config:
        orm_mode = True


class ListRatesModelResponse(BaseModel):
    rates: list[RateModelResponse]