from typing import Type
from fastapi import HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
import cloudinary.uploader

from src.conf.config import settings
from src.database.models import Photo, User
from src.database.db import get_db
from src.schemas import CreatePhotoModel



async def get_photos_by_user_id(user_id: int, db: Session) -> list[Type[Photo]]:
    """
    Method that returns the list of uploaded photos by the specific user.

    :param user_id: User identifier.
    :type user_id: int.
    :param db: db session object.
    :rtype db: Session.
    :return: The list of photos.
    :rtype: list[Type[Photo]]
    """
    photos = db.query(Photo).filter(Photo.created_by == user_id).all()
    return photos


def upload_photo_to_cloudinary(current_user: User, file: UploadFile = File())-> str:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    try:
        upload_result = cloudinary.uploader.upload(file.file,
                                                   public_id=f'PhotoShareApp/{current_user.user_name}/{file.filename}',)
        photo_url = upload_result['secure_url']
        return photo_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading photo: {str(e)}")


async def create_photo(description: str, current_user: User, db: Session, file: UploadFile = File()) -> Photo:
    photo_url = upload_photo_to_cloudinary(current_user=current_user, file=file)
    user_id = current_user.id
    photo = Photo(url=photo_url, description=description, created_by=user_id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo
