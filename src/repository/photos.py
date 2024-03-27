from typing import Type
from fastapi import HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary.uploader
from typing import Optional

from src.conf.config import settings
from src.database.models import Photo, User

import imghdr
import uuid
from typing import Optional
from sqlalchemy.exc import IntegrityError


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


def upload_photo_to_cloudinary(current_user: User, file: UploadFile = File(), description: Optional[str] = None) -> str:
    """
    The upload_photo_to_cloudinary function uploads a photo to the cloudinary server.
    It takes in three parameters: current_user, file, and description. The current_user parameter is used to
    create a unique public id for each user's photos on the cloudinary server, while the file
    parameter is used to upload an image from our local machine onto the cloudinary server. The description
    parameter is an optional parameter to provide additional information about the photo.

    :param current_user: User: Get the username of the user who is currently logged in
    :param file: UploadFile: Get the file uploaded by the user
    :param description: Optional[str]: Description of the photo (optional)
    :return: The url of the photo uploaded to cloudinary
    """
    # Перевірка формату файлу
    allowed_formats = ['jpeg', 'jpg', 'png']
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in allowed_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}. "
                                                    f"Supported formats are: {', '.join(allowed_formats)}")

    unique_filename = str(uuid.uuid4()) + '.' + file_extension

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    try:
        public_id = f'PhotoShareApp/{current_user.user_name}/{unique_filename}'

        upload_result = cloudinary.uploader.upload(file.file,
                                                   public_id=public_id)
        photo_url = upload_result['secure_url']
        return photo_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading photo: {str(e)}")


async def create_photo(description: str, current_user: User, db: Session, file: UploadFile = File()) -> Photo:
    """
    The create_photo function creates a new photo in the database.

    :param description: str: Specify the description of the photo
    :param current_user: User: Get the id of the user who is uploading a photo
    :param db: Session: Connect to the database
    :param file: UploadFile: Accept the file from the request
    :return: A photo object
    """
    photo_url = upload_photo_to_cloudinary(current_user=current_user, file=file)
    user_id = current_user.id
    photo = Photo(url=photo_url, description=description, created_by=user_id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo




