from __future__ import annotations

from fastapi import UploadFile, File, status, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
import redis
from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPBearer,
)
from src.conf.config import settings
from src.database.models import User
from src.repository import users as repository_users
from src.repository import photos as repository_photos
from src.database.db import get_db
from src.schemas import PhotoResponse

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()
r = redis.Redis(host=settings.redis_host, port=settings.redis_port)


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(description: Optional[str] = None, db: Session = Depends(get_db),
                       current_user: User = Depends(repository_users.get_current_user),
                       file: UploadFile = File()):
    if description is None:
        description = ""
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
def delete_photo(photo_id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(repository_users.get_current_user)):
    """
    Delete a photo from the database by its ID.
    """
    deleted_photo = repository_photos.delete_photo_by_id(
        photo_id=photo_id,
        current_user=current_user,
        db=db)
    if deleted_photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found")
    return PhotoResponse(
        id=deleted_photo.id,
        url=deleted_photo.url,
        description=deleted_photo.description,
        created_by=deleted_photo.created_by,
        created_at=deleted_photo.created_at,
    )


