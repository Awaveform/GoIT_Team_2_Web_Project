from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.orm import Session

from src.database.models.photo_comment import PhotoComment
from src.database.models.user import User
from src.schemas import CommentSchema


async def get_comment(
    comment_id: int, photo_id: int, db: Session
) -> PhotoComment | None:
    """
    Returns a comment object from the database.

    :param comment_id: int: Identifier of the comment to be retrieved.
    :type comment_id: int
    :param photo_id: int: Identifier of the associated photo.
    :type photo_id: int
    :param db: Session: Database session to be used for the operation.
    :type db: Session
    :return: A photocomment or None.
    :rtype: PhotoComment | None
    """
    db_request = Select(PhotoComment).filter_by(id=comment_id, photo_id=photo_id)
    result = db.execute(db_request)
    comment = result.scalar_one_or_none()
    return comment


async def create_comment(
    photo_id: int,
    comment: CommentSchema,
    current_user: User,
    db: Session,
) -> PhotoComment | None:
    """
    Creates a new comment in the database.

    :param photo_id: int: The identifier of the photo.
    :type photo_id: int
    :param comment: CommentSchema: The schema containing the comment data.
    :type comment: CommentSchema
    :param current_user: User: The user who is creating the comment.
    :type current_user: User
    :param db: Session: The database session.
    :type db: Session
    :return: A comment object if successfully created, otherwise None.
    :rtype: Union[PhotoComment, None]
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
) -> Sequence:
    """
    Returns a list of comments for the photo with the given id.
    The limit and offset parameters are used to paginate through results.

    :param photo_id: int: Filter the comments by photo id.
    :type photo_id: int
    :param limit: int: Limit the number of comments returned.
    :type limit: int
    :param offset: int: Specify the number of records to skip before starting to return rows.
    :type offset: int
    :param db: Session: Pass the database session to the function.
    :type db: Session
    :return: A sequence of photocomment objects.
    :rtype: Sequence[PhotoComment]
    """
    comments = (
        db.query(PhotoComment)
        .filter(PhotoComment.photo_id == photo_id)
        .order_by(PhotoComment.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return comments


async def update_comment(
    comment_id: int,
    photo_id: int,
    updated_comment: CommentSchema,
    current_user: User,
    db: Session,
):
    """
    Updates a comment in the database.

    :param comment_id: int: Identify the comment to be updated.
    :type comment_id: int
    :param photo_id: int: Find the comment that is associated with the photo.
    :type photo_id: int
    :param updated_comment: CommentSchema: Pass the updated comment to the function.
    :type updated_comment: CommentSchema
    :param current_user: User: Check if the user is logged in and has permissions to update a comment.
    :type current_user: User
    :param db: Session: Pass in the database session.
    :type db: Session
    :return: A comment object if successfully updated, otherwise None.
    :rtype: Optional[PhotoComment]
    """
    db_request = Select(PhotoComment).filter_by(
        id=comment_id, photo_id=photo_id, created_by=current_user.id
    )
    result = db.execute(db_request)
    comment = result.scalar_one_or_none()
    if comment:
        comment.comment = updated_comment.comment
        comment.updated_at = datetime.now()
        db.commit()
        db.refresh(comment)
    return comment


async def delete_comment(
    comment_id: int,
    photo_id: int,
    db: Session,
):
    """
    Deletes a comment from the database.

    :param comment_id: int: Identify the comment to be deleted
    :type comment_id: int
    :param photo_id: int: Filter the comments by photo_id
    :type photo_id: int
    :param db: Session: Access the database
    :type db: Session
    :return: A comment object
    :rtype: PhotoComment | None
    """
    db_request = Select(PhotoComment).filter_by(id=comment_id, photo_id=photo_id)
    comment = db.execute(db_request)
    comment = comment.scalar_one_or_none()
    if comment:
        db.delete(comment)
        db.commit()
    return comment
