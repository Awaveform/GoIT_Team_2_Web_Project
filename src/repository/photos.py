from typing import Type
from fastapi import HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary.uploader
import cloudinary.api

from src.conf.config import settings
from src.database.models import Photo, User, Role
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


async def get_photo_by_photo_id(
        photo_id: int, db: Session,
) -> Type[Photo] | None:
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

    :param current_user: Get the username of the user who is currently logged in
    :type current_user: User
    :param file: Get the file uploaded by the user
    :type file: UploadFile
    :return: The url of the photo uploaded to cloudinary
    :rtype: str
    """
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
        raise HTTPException(status_code=400, detail=f"Error uploading photo: {str(e)}")


async def create_photo(description: str, current_user: User, db: Session, file: UploadFile = File()) -> Photo:
    """
    The create_photo function creates a new photo in the database.

    :param description: Specify the description of the photo
    :type description: str
    :param current_user: Get the id of the user who is uploading a photo
    :type current_user: User
    :param db: Connect to the database
    :type db: Session
    :param file: Accept the file from the request
    :type file: UploadFile
    :return: A photo object
    :rtype: Photo
    """
    photo_url = _upload_photo_to_cloudinary(current_user=current_user, file=file)
    user_id = current_user.id
    photo = Photo(url=photo_url, description=description, created_by=user_id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def _get_public_id_from_url(photo_url: str) -> str:
    """
    The _get_public_id_from_url function takes a photo_url as an argument and returns the public_id of that image.

    :param photo_url: photo_url is a string that represents the URL of a photo on the cloudinary server
    :type photo_url: str
    :return: The public id of the photo
    :rtype: str
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

    :param photo_url: Pass the photo url to the function
    :type photo_url: str
    :return: A dictionary
    :rtype: dict
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


async def delete_photo_by_id(photo_id: int, db: Session):
    """
    The delete_photo_by_id function deletes a photo from the database and cloudinary.

    :param photo_id: Identify the photo to be deleted
    :type photo_id: int
    :param db: Access the database
    :type db: Session
    :return: The photo object
    :rtype: Photo
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    _delete_photo_from_cloudinary(photo_url=photo.url)
    db.delete(photo)
    db.commit()
    return photo


