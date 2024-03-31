from datetime import datetime
from typing import List

from sqlalchemy import Select, asc
from sqlalchemy.orm import Session

from src.database.models import User, PhotoComment
from src.schemas import CommentSchema

async def get_comment(comment_id:int, db:Session) -> PhotoComment | None:
    """
    The get_comment function returns a comment object from the database.
        
    :param comment_id:int: Find the comment in the database
    :type comment_id:int
    :param db:Session: Connect to the database
    :type db: Session
    :return: A photocomment or none
    :rtype: PhotoComment | None
    """
    stmt = Select(PhotoComment).filter_by(id=comment_id)
    result = db.execute(stmt)
    comment = result.scalar_one_or_none()
    return comment


async def create_comment (
        photo_id: int, 
        comment: CommentSchema, 
        current_user: User, 
        db: Session,
        ) -> PhotoComment | None:
    """
    The create_comment function creates a new comment in the database.
    
    :param photo_id: int: Specify the id of the photo
    :type photo_id: int
    :param comment: CommentSchema: Specify the comment of the photo
    :type comment: CommentSchema
    :param current_user: User: Get the id of the user who is uploading a photo
    :type current_user: User
    :param db: Session: Connect to the database
    :type db: Session
    :return: A comment object
    :rtype: PhotoComment | None
    """
    comment = PhotoComment(
        comment=comment.comment, 
        created_at=datetime.now(), 
        updated_at=None, 
        photo_id=photo_id, 
        created_by=current_user.id,
        )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
    

async def get_comments(
        photo_id: int, 
        limit: int, 
        offset: int,
        db: Session,
        ) -> List[PhotoComment]:
    """
    The get_comments function returns a list of comments for the photo with the given id.
        The limit and offset parameters are used to paginate through results.
        
    :param photo_id: int: Filter the comments by photo id
    :type photo_id: int
    :param limit: int: Limit the number of comments returned
    :type limit: int
    :param offset: int: Specify the number of records to skip before starting to return rows
    :type offset: int
    :param db: Session: Pass the database session to the function
    :type db: Session
    :return: A list of photocomment objects
    :rtype: List[PhotoComment] 
    """
    stmt = Select(PhotoComment).filter_by(photo_id=photo_id).order_by(asc(PhotoComment.id)).offset(offset).limit(limit)
    contacts =  db.execute(stmt)
    return contacts.scalars().all()


async def update_comment(
        comment_id: int, 
        photo_id: int,      
        updated_comment: CommentSchema, 
        current_user: User,
        db: Session,
        ):
    """
    The update_comment function updates a comment in the database.
    
    :param comment_id: int: Identify the comment to be updated
    :type comment_id: int
    :param photo_id: int: Find the comment that is associated with the photo
    :type photo_id: int
    :param updated_comment: CommentSchema: Pass the updated comment to the function
    :type updated_comment: CommentSchema
    :param current_user: User: Check if the user is logged in and has permissions to update a comment
    :type current_user: User
    :param db: Session: Pass in the database session
    :param : Get the id of the comment to be deleted
    :return: A comment object
    :doc-author: Trelent
    """
    stmt = Select(PhotoComment).filter_by(id=comment_id, photo_id=photo_id, created_by=current_user.id)
    result = db.execute(stmt)
    comment = result.scalar_one_or_none()
    if comment:
        comment.id = comment_id
        comment.comment = updated_comment.comment
        comment.created_at = comment.created_at
        comment.updated_at = datetime.now()
        comment.photo_id = comment.photo_id
        comment.created_by = comment.created_by
        db.commit()
        db.refresh(comment)
    return comment
