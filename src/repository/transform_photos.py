from __future__ import annotations

from typing import Type

import cloudinary
from cloudinary import uploader
from fastapi import HTTPException, status
from qrcode.image.styledpil import StyledPilImage
from sqlalchemy.orm import Session
import uuid

from src.conf.config import settings
from src.database.models import Photo
from src.schemas import TransformPhotoModel, PhotoQrCodeModel
from src.utils.data_convertor import get_enum_value
from src.utils.qr_code import generate_qr_code


async def _update_orig_photo_with_transformed_photo(
    db: Session,
    orig_photo: Photo,
    photo_url: str,
    updated_by: int,
    photo_description: str,
):
    """
    Method updates the original photo in the db with a transformed photo.

    :param db: DB instance.
    :type db: Session.
    :param orig_photo: Original photo.
    :type orig_photo: Photo.
    :param photo_url: Original photo URL.
    :type photo_url: str.
    :param updated_by: User who updated a photo.
    :type updated_by: int.
    :param photo_description: Photo description.
    :type photo_description: str.
    :return: Photo instance.
    :rtype: Photo.
    """
    orig_photo.url = photo_url
    orig_photo.updated_by = updated_by
    orig_photo.is_transformed = True
    orig_photo.description = photo_description
    db.add(orig_photo)
    db.commit()
    db.refresh(orig_photo)
    return orig_photo


async def _create_transformed_photo_in_db(
    db: Session,
    orig_photo: Photo,
    photo_url: str,
    updated_by: int,
    photo_description: str,
) -> Photo:
    """
    Method that creates the new row in the DB table public.photos for transformed photo.

    :param db: DB instance.
    :type db: Session.
    :param orig_photo: Original photo.
    :type orig_photo: Photo.
    :param photo_url: Original photo URL.
    :type photo_url: str.
    :param updated_by: User who updated a photo.
    :type updated_by: int.
    :param photo_description: Photo description.
    :type photo_description: str.
    :return: Photo instance.
    :rtype: Photo.
    """
    transformed_photo = Photo(
        url=photo_url,
        description=photo_description,
        created_by=updated_by,
        original_photo_id=orig_photo.id,
        is_transformed=True,
    )
    db.add(transformed_photo)
    db.commit()
    db.refresh(transformed_photo)
    return transformed_photo


async def _save_transformed_photo_to_db(
    db: Session,
    transformed_photo_url: str,
    updated_by: int,
    to_override_orig_photo,
    photo_description: str,
    orig_photo: Photo,
) -> Type[Photo] | None | Photo:
    """
    Method covers the logic of saving transformed photo in the DB.

    :param db: DB instance.
    :type db: Session.
    :param transformed_photo_url: URL of the transformed photo.
    :type transformed_photo_url: str.
    :param updated_by: User who updated a photo.
    :type updated_by: int.
    :param to_override_orig_photo: Parameter responsible for overriding an original
    photo or not.
    :type to_override_orig_photo: bool.
    :param photo_description: Photo description.
    :type photo_description: str.
    :param orig_photo: Original photo.
    :type orig_photo: Photo.
    :return: Photo instance.
    :rtype: Type[Photo] | None | Photo.
    """
    if to_override_orig_photo:
        return await _update_orig_photo_with_transformed_photo(
            db=db,
            orig_photo=orig_photo,
            photo_url=transformed_photo_url,
            updated_by=updated_by,
            photo_description=photo_description,
        )
    else:
        return await _create_transformed_photo_in_db(
            db=db,
            orig_photo=orig_photo,
            photo_url=transformed_photo_url,
            updated_by=updated_by,
            photo_description=photo_description,
        )


async def apply_transformation(
    photo: Photo,
    updated_by: int,
    body: TransformPhotoModel,
    db: Session,
) -> Type[Photo]:
    """
    Method that applies transformation for the existing photo and save info to DB to
    the table public.photos.
    :param photo: Original photo.
    :type photo: Photo.
    :param updated_by: User who updated a photo.
    :type updated_by: int.
    :param body: Transformation parameters.
    :type body: TransformPhotoModel.
    :param db: DB instance.
    :type db: Session.
    :return: Transformed photo.
    :rtype: Type[Photo].
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    try:
        transformed_img = uploader.upload(
            photo.url,
            public_id=str(uuid.uuid1()),
            overwrite=body.to_override,
            transformation=[
                {
                    k: get_enum_value(v)
                    for k, v in dict(body).items()
                    if k not in ("to_override", "description")
                }
            ],
        )
    except cloudinary.exceptions.Error as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error occurred during image transformation: '{str(err)}'",
        )
    transformed_url = transformed_img["secure_url"]
    return await _save_transformed_photo_to_db(
        db=db,
        transformed_photo_url=transformed_url,
        updated_by=updated_by,
        to_override_orig_photo=body.to_override,
        photo_description=body.description,
        orig_photo=photo,
    )


async def generate_photo_qr_code(
    photo: Photo, params: PhotoQrCodeModel
) -> StyledPilImage:
    """
    Method generates QR code for the photo URL.
    :param photo: Photo instance.
    :type photo: Photo.
    :param params: QR code image parameters.
    :type params: PhotoQrCodeModel.
    :return: QR code image.
    :rtype: StyledPilImage.
    """
    return generate_qr_code(
        photo_url=photo.url,
        module_drawer=params.module_drawer,
        color_mask=params.color_mask,
        box_size=params.box_size
    )
