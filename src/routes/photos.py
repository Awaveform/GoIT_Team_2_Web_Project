from __future__ import annotations

from fastapi import UploadFile, File, status, HTTPException
from typing import Optional

from redis.asyncio import Redis
from sqlalchemy.orm import Session
import redis
from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPBearer,
)

from src.cache.async_redis import get_redis
from src.database.models import User, Photo
from src.repository import users as repository_users
from src.repository import photos as repository_photos
from src.database.db import get_db
from src.schemas import PhotoResponse, PhotoUpdate

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(description: Optional[str] = None, db: Session = Depends(get_db),
                       current_user: User = Depends(repository_users.get_current_user),
                       file: UploadFile = File()):
    new_photo = await repository_photos.create_photo(
        description=description,
        current_user=current_user,
        db=db,
        file=file)

    return PhotoResponse(
        id=new_photo.id,
        url=new_photo.url,
        description=new_photo.description,
        created_by=new_photo.created_by,
        created_at=new_photo.created_at,
    )


@router.delete("/{photo_id}", response_model=PhotoResponse)
async def delete_photo(photo_id: int,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(repository_users.get_current_user),
                       r: Redis = Depends(get_redis)):

    current_user_role = await repository_users.get_user_role(
        user_id=current_user.id, db=db, r=r)

    photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id,
        db=db
        )

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found")

    if current_user_role.name == 'admin' or photo.created_by == current_user.id:
        deleted_photo = await repository_photos.delete_photo_by_id(
            photo=photo, db=db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden, only the owner or admin can delete the photo")

    return PhotoResponse(
        id=deleted_photo.id,
        url=deleted_photo.url,
        description=deleted_photo.description,
        created_by=deleted_photo.created_by,
        created_at=deleted_photo.created_at,
    )


async def update_photos_description(photo_id: int, description: str, current_user: User, db: Session) -> Photo:
    """
    The update_photos_description function updates the description of a photo in the database.

    :param photo_id: Specify which photo to update
    :type photo_id: int
    :param description: Update the description of a photo
    :type description: str
    :param current_user: Check if the user is an admin or not
    :type current_user: User
    :param db: Pass the database session to the function
    :type db: Session
    :return: The updated photo object
    :rtype: Photo
    """
    from src.repository.users import get_user_role
    user_role = await get_user_role(db=db, user_id=current_user.id)
    if user_role.name == 'admin':
        photo = db.query(Photo).filter(Photo.id == photo_id).first()
    else:
        photo = db.query(Photo).filter(Photo.id == photo_id, Photo.created_by == current_user.id).first()
    if photo:
        photo.description = description
        photo.description = description
        db.commit()
        db.refresh(photo)
    return photo


@router.put("/photos/{photo_id}/description", response_model=PhotoUpdate)
async def update_photo_description(
        photo_id: int,
        new_description: Optional[str] = None,
        current_user: User = Depends(repository_users.get_current_user),
        db: Session = Depends(get_db),
        r: Redis = Depends(get_redis)):

    current_user_role = await repository_users.get_user_role(
        user_id=current_user.id, db=db, r=r)

    photo = await repository_photos.get_photo_by_photo_id(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if current_user_role.name == 'admin' or photo.created_by == current_user.id or current_user_role.name == 'moderator':
        updated_photo = await repository_photos.update_photo_description(photo, new_description, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden, only the owner, admin or moderator can updating photo description")
    return PhotoUpdate(
        id=updated_photo.id,
        description=updated_photo.description,
        created_by=updated_photo.created_by,
        created_at=updated_photo.created_at,
        updated_at=updated_photo.updated_at,
        url=updated_photo.url
    )