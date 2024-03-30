from datetime import datetime

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
    
