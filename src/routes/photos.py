from __future__ import annotations
from fastapi import HTTPException, UploadFile, File, Depends, status, Path
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


@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(photo_id: int,
              db: Session = Depends(get_db)):
    photo = repository_photos.get_photo_by_id(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return PhotoResponse(
        id=photo.id,
        url=photo.url,
        description=photo.description,
        created_by=photo.created_by,
        created_at=photo.created_at,
    )


@router.delete("/{photo_id}", response_model=bool)
def delete_photo(photo_id: int = Path(..., title="The ID of the photo to delete"),
                 db: Session = Depends(get_db)):
    """
    Delete a photo from the database by its ID.
    """
    deleted = repository_photos.delete_photo_by_id(photo_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Photo not found")
    return True


@router.get("/{photo_id}/url", response_model=str)
def get_photo_url(photo_id: int = Path(..., title="The ID of the photo"),
                  db: Session = Depends(get_db)):
    """
    Get the URL of a photo by its ID.
    """
    photo_url = repository_photos.get_photo_url_by_id(photo_id, db)
    if not photo_url:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo_url
