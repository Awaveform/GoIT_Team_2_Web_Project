from typing import Type
from fastapi import HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary.uploader
import cloudinary.api

from src.conf.config import settings
from src.database.models import Photo, User
import uuid


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


async def get_photo_by_photo_id(photo_id: int, db: Session) -> Photo:
    """
    Method that returns the uploaded photo by the photo identifier.

    :param photo_id: Photo identifier.
    :type photo_id: int.
    :param db: db session object.
    :rtype db: Session.
    :return: Photo.
    :rtype: Photo
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    return photo


# TODO: AR refactor -move logic and exeption to routs
def _upload_photo_to_cloudinary(current_user: User, file: UploadFile = File()) -> str:
    """
    The upload_photo_to_cloudinary function uploads a photo to the cloudinary server.
    It takes in three parameters: current_user, file, and description. The current_user parameter is used to
    create a unique public id for each user's photos on the cloudinary server, while the file
    parameter is used to upload an image from our local machine onto the cloudinary server. The description
    parameter is an optional parameter to provide additional information about the photo.

    :param current_user: User: Get the username of the user who is currently logged in
    :param file: UploadFile: Get the file uploaded by the user
    :return: The url of the photo uploaded to cloudinary
    """
    # Перевірка формату файлу
    allowed_formats = ['jpeg', 'jpg', 'png']
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in allowed_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}. "
                                                    f"Supported formats are: {', '.join(allowed_formats)}")

    unique_filename = str(uuid.uuid4())

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
    photo_url = _upload_photo_to_cloudinary(current_user=current_user, file=file)
    user_id = current_user.id
    photo = Photo(url=photo_url, description=description, created_by=user_id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def _get_public_id_from_url(photo_url):
    """
    The _get_public_id_from_url function takes a photo_url as input and returns the public_id of that image.
    The public id is used to delete an image from Cloudinary.

    :param photo_url: Get the public id of the photo
    :return: The public id of a photo given its url
    """
    parts = photo_url.split('/')
    index = parts.index('PhotoShareApp')
    parts = parts[index:]
    parts[-1] = parts[-1].split('.')[0]
    public_id = '/'.join(parts)
    return public_id


def _delete_photo_from_cloudinary(photo_url: str):
    """
    The _delete_photo_from_cloudinary function takes in a photo_url parameter, which is the URL of the photo to be deleted.
    It then uses Cloudinary's Python SDK to delete that image from Cloudinary
    :param photo_url: str: Pass the photo url to the function
    :return: A dictionary
    """

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    public_ids = _get_public_id_from_url(photo_url)
    image_delete_result = cloudinary.api.delete_resources(public_ids, resource_type="image", type="upload")
    print(image_delete_result)


def delete_photo_by_id(photo_id: int, current_user: User, db: Session):
    """
    The delete_photo_by_id function deletes a photo from the database.
        Args:
            photo_id (int): The id of the photo to be deleted.
            current_user (User): The user who is deleting the photo. This is used for authorization purposes, as only
                photos created by that user can be deleted by them.

    :param photo_id: int: Identify the photo to be deleted
    :param current_user: User: Make sure that the user is logged in and has access to delete a photo
    :param db: Session: Access the database
    :return: The photo that was deleted
    """
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.created_by == current_user.id).first()

    if photo:
        try:
            _delete_photo_from_cloudinary(photo_url=photo.url)
        except Exception as e:
            print(f"Error deleting photo from Cloudinary: {e}")
        db.delete(photo)
        db.commit()
    return photo


