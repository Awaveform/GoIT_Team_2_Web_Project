from __future__ import annotations
from fastapi import Query, status
from sqlalchemy.orm import Session
import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import (HTTPBearer)
from src.conf.config import settings
from src.database.models import User
from src.repository import (
    comments as repository_comments, 
    photos as repository_photos,
    users as repository_users
    )
from src.database.db import get_db
from src.schemas import CommentResponse, CommentSchema

router = APIRouter(prefix="/photos", tags=["comments"])
security = HTTPBearer()
r = redis.Redis(
    host=settings.redis_host, 
    port=settings.redis_port,
    )


@router.post("/{photo_id}/comments", 
             response_model=CommentResponse, 
             status_code=status.HTTP_201_CREATED)
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


@router.get('/{photo_id}/comments', response_model=list[CommentResponse])
async def get_comments(
    photo_id: int, 
    limit: int = Query(10, ge=10, le=500), 
    offset: int = Query(0, ge=0), 
    db: Session = Depends(get_db),
    ):
    """
    The get_comments function returns a list of comments for the specified photo.
        The function takes in an integer representing the photo_id, and two optional parameters: limit and offset. 
        Limit is used to specify how many comments should be returned at once, while offset specifies where in the list of all comments to start returning from.
    
    :param photo_id: int: Get the comments for a specific photo
    :param limit: int: Limit the number of comments returned
    :param ge: Specify the minimum value of a parameter
    :param le: Set the maximum value of limit
    :param offset: int: Specify the offset of the comments that are returned
    :param ge: Check if the limit is greater than or equal to 10
    :param db: AsyncSession: Get the database session
    :return: A list of commentresponse objects
    """
    comments = await repository_comments.get_comments(photo_id, limit, offset, db)
    if comments:
        result = []
        for comment in comments:
            result.append(
                CommentResponse(
                    id=comment.id,
                    comment=comment.comment,
                    created_at= comment.created_at,
                    photo_id= comment.photo_id,
                    created_by= comment.created_by,
                    )
                )         
    else:
        #checks offset parameter 
        offset = 0
        comments = await repository_comments.get_comments(photo_id, limit, offset, db)
        if comments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Number of comments for the photo {photo_id} is less than specified in offset parameter.",
        )
        else: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The photo {photo_id} does not exist.",
            )
    return result