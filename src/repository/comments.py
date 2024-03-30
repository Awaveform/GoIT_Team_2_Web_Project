from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.models import Photo, User
from src.database.models import PhotoComment


async def create_comment (photo_id: int, 
                          comment: str,
                          current_user: User, 
                          db: Session
                          ) -> PhotoComment | None:
    """
    The create_comment function creates a new comment in the database.
    
    :param photo_id: int: Specify the id of the photo
    :param comment: str: Specify the comment of the photo
    :param current_user: User: Get the id of the user who is uploading a photo
    :param db: Session: Connect to the database
    :return: A comment object
    """
    comment = PhotoComment(comment=comment.comment, 
                        created_at=datetime.now(), 
                        updated_at=None, 
                        photo_id=photo_id, 
                        created_by=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
    
