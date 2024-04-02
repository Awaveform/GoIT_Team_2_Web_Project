from __future__ import annotations
from fastapi import UploadFile, File, status, HTTPException


from redis.asyncio import Redis
from typing import Optional, List, Union
from sqlalchemy.orm import Session
import redis
from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPBearer,
)

from src.cache.async_redis import get_redis
from src.database.models import User
from src.conf.config import settings
from src.database.models import User, Photo
from src.database.models import User, Role
from src.repository import users as repository_users
from src.repository import photos as repository_photos
from src.database.db import get_db
from src.schemas import PhotoResponse

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()


@router.get("/", response_model=Union[List[PhotoResponse], PhotoResponse])
async def get_photos_by_user_id_or_all(
        db: Session = Depends(get_db),
        user_id: Optional[int] = None,
        photo_id: Optional[int] = None,
        current_user: User = Depends(repository_users.get_current_user),
        limit: int = 10,
        skip: int = 0):

    if user_id and photo_id:
        photos = await repository_photos.get_photo_by_photo_id_and_user_id(
            user_id=user_id, photo_id=photo_id, db=db)
        if photos is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Photo with photo_id - {photo_id} for user- {user_id} not found")

    if user_id and photo_id is None:
        photos = await repository_photos.get_photos_by_user_id(
            user_id=user_id, db=db, limit=limit, skip=skip)
        if not photos:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Photos for {user_id} not found")

    if user_id is None and photo_id:
        photos = await repository_photos.get_photo_by_photo_id(
            photo_id=photo_id, db=db)
        if photos is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Photo with photo_id -{photo_id} not found")

    if user_id is None and photo_id is None:
        photos = await repository_photos.get_photos_by_user_id(
            db=db,
            user_id=current_user.id,
            limit=limit,
            skip=skip)
        if photos is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Photos for {current_user.id} not found")
    return photos


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
        deleted_photo = await repository_photos.delete_photo(
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




