from __future__ import annotations

from fastapi import UploadFile, File, status, HTTPException
from typing import Optional, List

from redis.asyncio import Redis
from sqlalchemy.orm import Session
import redis
from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPBearer,
)

from src.cache.async_redis import get_redis
from src.database.models import User, Tag, Photo
from src.repository import users as repository_users
from src.repository import photos as repository_photos
from src.database.db import get_db
from src.schemas import PhotoResponse,TagResponse, PhotoResponseWithTags

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


@router.post("/photos/{photo_id}/tags", response_model=PhotoResponseWithTags)
async def add_tags(
        photo_id: int,
        tag_name: str,
        current_user: User = Depends(repository_users.get_current_user),
        db: Session = Depends(get_db)):

    # Перевірка, що фотографія існує
    photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id,
        db=db
    )
    if not photo:
        raise HTTPException(status_code=404, detail=f"Photo with photo_id- {photo_id} not found")

    if current_user.id != photo.created_by:
        raise HTTPException(status_code=403, detail="Forbidden, only the owner can add tags to the photo")

    # Отримання списку тегів на фотографії
    existing_tags = await repository_photos.get_tags_by_photo_id(photo.id, db)
    existing_tag_names = [tag.name for tag in existing_tags]

    for tag_name in existing_tag_names:
        print(tag_name)

    if tag_name in existing_tag_names:
        raise HTTPException(status_code=400, detail="Tag already exists")

    # Перевірка, що кількість тегів не перевищує 5
    if len(existing_tags) + 1 > 5:
        raise HTTPException(status_code=400, detail="The number of tags cannot exceed 5")

    tag = await repository_photos.add_tag_by_name(tag_name=tag_name, current_user=current_user, db=db)

    photo_with_tags = await repository_photos.add_tags_to_photo(photo=photo, tag=tag, db=db)
    return photo_with_tags
