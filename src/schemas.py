from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

from src.enums import (
    Roles,
    QrModuleDrawer,
    QrColorMask,
    PhotoEffect,
    PhotoCrop,
    PhotoGravity,
)


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


class TransformPhotoModel(BaseModel):
    to_override: bool = False
    description: str | None = Field(min_length=5, title="Photo description")
    effect: PhotoEffect | None = PhotoEffect.BLUR.value
    angle: int | None = Field(gt=0, le=360, title="Angle of photo rotation")
    crop: PhotoCrop | None = PhotoCrop.FILL.value
    gravity: PhotoGravity | None = PhotoGravity.AUTO.value
    width: int | None = Field(title="Photo width", gt=0, le=1000)
    height: int | None = Field(title="Photo height", gt=0, le=1000)


class TransformedPhotoModelResponse(BaseModel):
    id: int
    url: str
    description: str | None
    created_at: datetime
    updated_at: datetime | None
    created_by: int
    updated_by: int | None
    original_photo_id: int | None
    is_transformed: bool | None

    class Config:
        orm_mode = True


class PhotoQrCodeModel(BaseModel):
    module_drawer: QrModuleDrawer = QrModuleDrawer.ROUNDED
    color_mask: QrColorMask = QrColorMask.SOLID
    box_size: int = Field(title="QR code box size", gt=0, default=10)


class PhotoQrCodeModelResponse(BaseModel):
    qr_code: str


class RateModel(BaseModel):
    grade: int = Field(ge=1, le=5)


class RateModelResponse(RateModel):
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True


class ListRatesModelResponse(BaseModel):
    rates: list[RateModelResponse]


class DeleteRatesResponse(BaseModel):
    detail: str