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


async def get_comments(photo_id: int, limit: int, offset: int, db: AsyncSession):
    """
    The get_comments function returns a list of comments for the photo with the given id.
        
    
    :param photo_id: int: Filter the comments by photo_id
    :param limit: int: Limit the number of comments returned
    :param offset: int: Specify the number of comments to skip before returning
    :param db: AsyncSession: Pass the database connection to the function
    :return: A list of photocomment objects
    """
    stmt = select(PhotoComment).filter_by(photo_id=photo_id).offset(offset).limit(limit)
    contacts =  db.execute(stmt)
    return contacts.scalars().all()


async def update_comment(comment_id: int, body: CommentSchema, user: User, db: AsyncSession):
    stmt = select(PhotoComment).filter_by(comment_id=comment_id)
    result = db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment and comment.created_by == user.id:
        comment.comment = body.comment
        db.commit()
        await db.refresh(comment)
    return comment
    


async def delete_comment(photo_id: int, comment_id:int, db: AsyncSession):
    stmt = select(PhotoComment).filter_by(id=photo_id, comment_id=comment_id)
    comment = await db.execute(stmt)
    comment = comment.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment