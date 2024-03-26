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
    """
    The create_comment function creates a new comment for the photo with the chosen id.
        The created_by field is automatically set to the user who made this request.
    
    :param photo_id: int: Pass the photo id to the create_comment function
    :param body: CommentSchema: Validate the data that is sent to the api
    :param created_by: User: Get the user that is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A commentresponse object
    """
    comment = await repository_comments.create_comment(body, photo_id, created_by.id, db)
    return CommentResponse(id=comment.id,
    comment=comment.comment,
    created_at= comment.created_at,
    photo_id= comment.photo_id,
    created_by= comment.created_by)
    