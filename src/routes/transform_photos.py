from io import BytesIO
from typing import Type

from fastapi import APIRouter, status, Depends, HTTPException
from qrcode.image.styledpil import StyledPilImage
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from src.database.db import get_db
from src.database.models import Photo, User
from src.repository.users import get_current_user
from src.schemas import (
    TransformedPhotoModelResponse,
    TransformPhotoModel,
    PhotoQrCodeModel,
    PhotoQrCodeModelResponse,
)
from src.repository import transform_photos as repository_transform
from src.repository import photos as repository_photos

router = APIRouter(prefix="/transform", tags=["transform"])


@router.post(
    "/{photo_id}",
    response_model=TransformedPhotoModelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def transform_photo(
    photo_id: int,
    body: TransformPhotoModel = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Method makes photo transformation with storing data to DB.
    :param body: Transformation parameters.
    :type body: TransformPhotoModel.
    :param photo_id: Original photo identifier.
    :type photo_id: int.
    :param db: DB instance.
    :type db: Session.
    :param current_user: Authorized user.
    :type current_user: User.
    :return: Transformed photo instance.
    :rtype: TransformedPhotoModelResponse
    """
    photo: Photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id, db=db
    )
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id {photo_id} wasn't found",
        )
    transformed_photo: Type[Photo] = await repository_transform.apply_transformation(
        photo=photo, updated_by=current_user, body=body, db=db
    )
    return TransformedPhotoModelResponse(
        id=transformed_photo.id,
        url=transformed_photo.url,
        description=transformed_photo.description,
        created_at=transformed_photo.created_at,
        updated_at=transformed_photo.updated_at,
        created_by=transformed_photo.created_by,
        updated_by=transformed_photo.updated_by,
        original_photo_id=transformed_photo.original_photo_id,
        is_transformed=transformed_photo.is_transformed,
    )


@router.post(
    "/{photo_id}/qr_code",
    response_model=PhotoQrCodeModelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def get_photo_url_qr_code(
    photo_id: int,
    body: PhotoQrCodeModel = Depends(),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Method generates QR code with an embedded link inside it.

    :param photo_id: Photo identifier.
    :type photo_id: int.
    :param body: QR code params.
    :type body: PhotoQrCodeModel
    :param db: DB session instance.
    :type db: Session.
    :param _: Authorized user info.
    :type _: User.
    :return: QR code image.
    :rtype: StreamingResponse.
    """
    photo: Photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id, db=db
    )
    img: StyledPilImage = await repository_transform.generate_photo_qr_code(
        photo=photo, params=body
    )
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return StreamingResponse(img_bytes, media_type="image/jpeg")
