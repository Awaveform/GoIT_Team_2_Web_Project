from __future__ import annotations
from fastapi import status
from typing import Optional
from sqlalchemy.orm import Session
import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import (HTTPBearer)
from src.conf.config import settings
from src.database.models import User
from src.repository import (
    comments as repository_comments, 
    photos as repository_photos,
    users as repository_users
    )
from src.database.db import get_db
from src.schemas import CommentResponse, CommentSchema

router = APIRouter(prefix="/photos", tags=["comments"])
security = HTTPBearer()
r = redis.Redis(host=settings.redis_host, port=settings.redis_port)


@router.post("/{photo_id}/comments", 
             response_model=CommentResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_comment(photo_id: int,
                         comment: CommentSchema, 
                         current_user: User = Depends(repository_users.get_current_user),
                         db: Session = Depends(get_db)):
    
    photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id,
        db=db
    )

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The photo {photo_id} does not exist."
        )

    if not comment.comment.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment should not be empty."
        )
    
    
    new_comment = await repository_comments.create_comment(
        comment=comment,
        photo_id=photo_id,
        current_user=current_user,
        db=db)
    
    return CommentResponse(
        id=new_comment.id,
        comment=new_comment.comment,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at,
        photo_id=new_comment.photo_id,
        created_by=new_comment.created_by,
    )
