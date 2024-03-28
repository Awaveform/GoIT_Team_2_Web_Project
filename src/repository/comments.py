from datetime import datetime
from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from src.database.models import PhotoComment, User, Photo
from src.schemas import CommentSchema, CommentResponse
from src.database.db import get_db

async def create_comment(body: CommentSchema, 
                         photo_id: int, 
                         created_by: int, 
                         db: AsyncSession = Depends(get_db)):
    """
    The create_comment function creates a new comment for a photo.
    Args:
        body (CommentSchema): The CommentSchema object containing the comment to be created.
        photo_id (int): The id of the photo that is being commented on.
        created_by (int): The id of the user who is creating this comment.
    Returns: 
        PhotoComment: A PhotoComment object representing the newly-created comment.
    """
    
    try:
        photo = db.execute(select(Photo).filter(Photo.id == photo_id))
        photo = photo.scalar_one()
    except NoResultFound:
        raise HTTPException(status_code=400, detail=f"Photo with id {photo_id} not found")

    try:
        user = db.execute(select(User).filter(User.id == created_by))
        user = user.scalar_one()
    except NoResultFound:
        raise HTTPException(status_code=400, detail=f"User with id {created_by} not found")

    date = datetime.now()
    comment_dct = {'comment': body.comment, "photo_id": photo_id, "created_by": created_by}
    comment = PhotoComment(**comment_dct)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

