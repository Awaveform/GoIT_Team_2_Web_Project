from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from src.database.models import PhotoComment, User, Photo
from src.schemas import CommentSchema


async def get_photo_by_id(db: Session, photo_id: int) -> Photo | None:
    """
    The get_photo_by_id function returns a photo object from the database based on its id.
        Args:
            db (Session): The SQLAlchemy session to use for querying the database.
            photo_id (int): The id of the photo to retrieve from the database.
        Returns:
            Photo | None: A single Photo object or None if no matching record is found in the database.
    
    :param db: Session: Create a connection to the database
    :param photo_id: int: Specify which photo to get from the database
    :return: A photo object or none
    """
    try:
        photo = db.execute(select(Photo).filter(Photo.id == photo_id))
        return photo.scalar_one()
    except NoResultFound:
        return None


async def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    The get_user_by_id function returns a user object from the database based on the user_id parameter.
    If no such user exists, it will return None.
    
    :param db: Session: Access the database
    :param user_id: int: Identify the user in the database
    :return: A user object
    """
    try:
        user = db.execute(select(User).filter(User.id == user_id))
        return user.scalar_one()
    except NoResultFound:
        return None


async def create_comment(
    body: CommentSchema, photo_id: int, created_by: int, db: Session
):
    """
    The create_comment function creates a new comment for a photo.
        Args:
            body (CommentSchema): The CommentSchema object containing the comment to be created.
            photo_id (int): The id of the photo that will have this comment added to it.
            created_by (int): The id of the user who is creating this comment.
        Returns:
            PhotoComment: A PhotoComment object representing the newly-created database entry for this new Comment.
    
    :param body: CommentSchema: Validate the request body
    :param photo_id: int: Get the photo by id
    :param created_by: int: Get the user who created the comment
    :param db: Session: Pass the database session to the function
    :return: The comment object
    """
    photo = await get_photo_by_id(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=400, detail=f"Photo with id {photo_id} not found"
        )

    user = await get_user_by_id(db, created_by)
    if user is None:
        raise HTTPException(
            status_code=400, detail=f"User with id {created_by} not found"
        )

    try:
        user = db.execute(select(User).filter(User.id == created_by))
        user = user.scalar_one()
    except NoResultFound:
        raise HTTPException(
            status_code=400, detail=f"User with id {created_by} not found"
        )

    comment_dct = {
        "comment": body.comment,
        "photo_id": photo_id,
        "created_by": created_by,
    }
    comment = PhotoComment(**comment_dct)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment