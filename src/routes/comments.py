from __future__ import annotations
from typing import Union
from fastapi import Query, status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from src.database.models.user import User
from src.enums import Roles
from src.repository import (
    comments as repository_comments,
    photos as repository_photos,
    users as repository_users,
)
from src.database.db import get_db
from src.repository.users import get_current_user
from src.schemas import CommentResponse, CommentSchema
from src.security.role_permissions import RoleChecker

router = APIRouter(prefix="/photos", tags=["comments"])
security = HTTPBearer()


@router.post(
    "/{photo_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    photo_id: int,
    comment: CommentSchema,
    current_user: User = Depends(repository_users.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The create_comment function creates a new comment for the photo with the given id.
        The function requires that you are logged in and that you provide a valid comment.


    :param photo_id: int: Get the photo that is being commented on
    :type photo_id: int
    :param comment: CommentSchema: Validate the request body
    :type comment: CommentSchema
    :param current_user: User: Get the user who is currently logged in
    :type current_user: User
    :param db: Session: Create a database session
    :type db: Session
    :return: A commentresponse object
    :rtype: CommentResponse
    """
    photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id,
        db=db,
    )

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The photo {photo_id} does not exist.",
        )

    if not comment.comment.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment should not be empty.",
        )

    new_comment = await repository_comments.create_comment(
        comment=comment,
        photo_id=photo_id,
        current_user=current_user,
        db=db,
    )

    return CommentResponse(
        id=new_comment.id,
        comment=new_comment.comment,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at,
        photo_id=new_comment.photo_id,
        created_by=new_comment.created_by,
    )


@router.get("/{photo_id}/comments", response_model=Union[list[CommentResponse], dict])
async def get_comments(
    photo_id: int,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Union[list[CommentResponse], dict]:
    """
    The get_comments function returns a list of comments for the specified photo.
        The function takes in three parameters:
            - photo_id (int): id of the photo to get comments from,
            - limit (int): number of comments to return, default is 10 and max is 500,
            - offset (int): number of records to skip before returning results. Default value is 0.

    :param photo_id: int: Specify the photo for which we want to get comments
    :type photo_id: int
    :param limit: int: Limit the number of comments returned
    :type limit: int
    :param ge: Check if the limit parameter is greater than or equal to 10
    :type ge: int
    :param le: Set the maximum value of a parameter
    :type le: int
    :param offset: int: Specify the number of comments to skip
    :type offset: int
    :param ge: Check if the limit parameter is greater than or equal to 10
    :type ge: int
    :param db: Session: Access the database
    :type db: Session
    :return: A dictionary with list of comments for a particular photo
    :rtype:  Union[list[CommentResponse], dict]
    """
    comments = await repository_comments.get_comments(photo_id, limit, offset, db)

    if comments:
        return {
            "comments": [
                CommentResponse(
                    id=comment.id,
                    comment=comment.comment,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    photo_id=comment.photo_id,
                    created_by=comment.created_by,
                )
                for comment in comments
            ]
        }

    if not await repository_photos.get_photo_by_photo_id(photo_id=photo_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The photo {photo_id} does not exist.",
        )

    if offset > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Offset parameter is greater than the total number of comments for photo {photo_id}.",
        )
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{photo_id}/comments")
async def update_comment(
    comment_id: int,
    photo_id: int,
    updated_comment: CommentSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    The update_contact function updates a comment by its id.

    :param comment_id: int: Get the comment by id
    :type comment_id: int
    :param photo_id: int: Check if the photo exists
    :type photo_id: int
    :param updated_comment:CommentSchema: Pass the updated comment to the function
    :type updated_comment: CommentSchema
    :param current_user: User: Get the current user
    :type current_user: User
    :param db: Session: Pass the database session to the function
    :type db: Session
    :return: A commentschema object or None
    :rtype: CommentSchema | None
    """
    photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id,
        db=db,
    )

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The photo {photo_id} does not exist.",
        )

    comment = await repository_comments.get_comment(comment_id, photo_id, db)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No such comment to photo {photo_id}",
        )

    if comment.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Comment's edition available for owner of the photo only.",
        )

    if not updated_comment.comment.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment should not be empty.",
        )

    comment = await repository_comments.update_comment(
        comment_id,
        photo_id,
        updated_comment,
        current_user,
        db,
    )
    return comment


@router.delete("/{photo_id}/comments", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    photo_id: int,
    db: Session = Depends(
        RoleChecker(allowed_roles=[Roles.ADMIN.value, Roles.MODERATOR.value])
    ),
):
    """
    The delete_comment function deletes a comment from the database.

    :param comment_id: int: Identify the comment that is to be deleted
    :type comment_id: int
    :param photo_id: int: Get the photo_id of the comment that is being deleted
    :type photo_id: int
    :param db: Session: Pass a database session to the function
    :type db: Session
    :return: None
    """
    await repository_comments.delete_comment(comment_id, photo_id, db)
