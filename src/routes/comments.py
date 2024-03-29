from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
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
    db: Session = Depends(get_db),
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


@router.get("/{photo_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    photo_id: int,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    The get_comments function returns a list of comments for the specified photo.

    :param photo_id: int: Get the comments for a specific photo
    :param limit: int: Limit the number of comments returned
    :param ge: Specify the minimum value of the parameter
    :param le: Limit the number of comments that can be returned at once
    :param offset: int: Skip the first n comments
    :param ge: Set a minimum value for the limit and offset parameters
    :param db: Session: Get the database session
    :param : Limit the number of comments that are returned
    :return: A list of commentresponse objects
    """
    comments = await repository_comments.get_comments(photo_id, limit, offset, db)
    result = []
    for comment in comments:
        result.append(
            CommentResponse(
                comment_id=comment.id,
                comment=comment.comment,
                created_at=comment.created_at,
                photo_id=comment.photo_id,
                created_by=comment.created_by,
            )
        )
    return result
