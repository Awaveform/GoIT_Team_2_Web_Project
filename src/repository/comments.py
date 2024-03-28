from datetime import timedelta, datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import PhotoComment, User
from src.schemas import CommentSchema, CommentResponse
from src.database.db import get_db

async def create_comment(body: CommentSchema, photo_id: int, created_by: int,  db: AsyncSession):
    """
    The create_comment function creates a new comment for a photo.
        Args:
            body (CommentSchema): The CommentSchema object containing the comment to be created.
            photo_id (int): The id of the photo that is being commented on.
            created_by (int): The id of the user who is creating this comment.
        Returns: 
            PhotoComment: A PhotoComment object representing the newly-created comment.
    
    :param body: CommentSchema: Get the comment from the request body
    :param photo_id: int: Identify the photo that the comment is being added to
    :param created_by: int: Specify the user who created the comment
    :param db: AsyncSession: Pass the database connection to the function
    :return: A comment object
   """
    date = datetime.now()
    comment_dct = {'comment':body.comment, 
                   "photo_id": photo_id, 
                   "created_by": created_by}
    comment = PhotoComment(**comment_dct)
    if db.add(comment):
        db.commit()
        db.refresh(comment)
        return comment
    else:
        return None
