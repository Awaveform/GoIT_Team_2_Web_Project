from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer

from src.repository.users import get_current_user
from src.database.models import User
from src.database.db import get_db
from src.repository import comments as repository_comments
from src.schemas import CommentSchema, CommentResponse

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()


@router.post(
    "/{photo_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    photo_id: int,
    body: CommentSchema,
    created_by: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The create_comment function creates a comment for a photo.
        Args:
            photo_id (int): The id of the photo to which the comment is being added.
            body (CommentSchema): A CommentSchema object containing the new comment's details. 
                This includes its text, and who created it.
    
    :param photo_id: int: Identify the photo that we want to comment on
    :param body: CommentSchema: Validate the request body
    :param created_by: User: Get the user that is currently logged in
    :param db: AsyncSession: Get the database session
    :param : Get the user who is logged in
    :return: Commentresponse
    """
    if body.comment.strip():
        comment = await repository_comments.create_comment(
            body, photo_id, created_by.id, db
        )
        if comment:
            return CommentResponse(
                comment_id=comment.id,
                comment=comment.comment,
                created_at=comment.created_at,
                photo_id=comment.photo_id,
                created_by=comment.created_by,
            )
        else:
            raise HTTPException(status_code=400, detail="Wrong request")
    else:
        raise HTTPException(status_code=400, detail="Comment can not be blank")