from datetime import datetime
from typing import List

from sqlalchemy import Select
from sqlalchemy.orm import Session

from src.database.models import User, PhotoComment
from src.schemas import CommentSchema

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
    :param limit: int: Limit the number of comments returned
    :param offset: int: Specify the number of records to skip before starting to return rows
    :param db: Session: Pass the database session to the function
    type db: Session
    :param : Get the comments of a photo
    :return: A list of photocomment objects
    :rtype: List[PhotoComment]
    """
    stmt = Select(PhotoComment).filter_by(photo_id=photo_id).offset(offset).limit(limit)
    contacts =  db.execute(stmt)
    return contacts.scalars().all()
