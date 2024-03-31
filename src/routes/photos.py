from __future__ import annotations
from fastapi import UploadFile, File, status, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
import redis
from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPBearer,
)
from src.conf.config import settings
from src.database.models import User, Photo
from src.repository import users as repository_users
from src.repository import photos as repository_photos
from src.database.db import get_db
from src.schemas import PhotoResponse

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()


@router.get("/userID/{user_id}", response_model=List[PhotoResponse])
async def get_users_photos_by_id(user_id: int, db: Session = Depends(get_db)):
    photos = await repository_photos.get_photos_by_user_id(user_id, db)
    if not photos:
        raise HTTPException(status_code=404, detail="No photos found for the user")
    photo_responses = []
    for photo in photos:
        photo_responses.append(PhotoResponse(
            id=photo.id,
            url=photo.url,
            description=photo.description,
            created_by=photo.created_by,
            created_at=photo.created_at,
        ))
    return photo_responses


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int,
                    db: Session = Depends(get_db)):
    photo = await repository_photos.get_photo_by_photo_id(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return PhotoResponse(
        id=photo.id,
        url=photo.url,
        description=photo.description,
        created_by=photo.created_by,
        created_at=photo.created_at,
    )


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




