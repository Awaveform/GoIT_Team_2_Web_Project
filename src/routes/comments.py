from datetime import date

from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer

from src.repository.users import get_current_user
from src.database.models import User
from src.database.db import get_db
from src.repository import comments as repository_comments
from src.schemas import CommentSchema, CommentResponse

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()

@router.post('/{photo_id}/comments', response_model=CommentResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_comment(photo_id: int, body: CommentSchema, 
                         created_by: User = Depends(get_current_user), 
                         db: AsyncSession = Depends(get_db)):
    comment = await repository_comments.create_comment(body, photo_id, created_by.id, db)
    return comment