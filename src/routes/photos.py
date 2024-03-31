from __future__ import annotations
from fastapi import UploadFile, File, status
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
