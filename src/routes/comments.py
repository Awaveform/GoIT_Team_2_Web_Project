from datetime import date

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer

from src.repository.users import get_current_user
from src.database.models import User
from src.database.db import get_db
from src.repository import comments as repository_comments
from src.schemas import CommentSchema, CommentResponse

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()

@router.post('/{photo_id}/comments', response_model=CommentResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_comment(photo_id: int, body: CommentSchema, 
                         created_by: User = Depends(get_current_user), 
                         db: AsyncSession = Depends(get_db)):

    """ 
    The create_comment function creates a comment for a photo.
        Args:
            photo_id (int): The id of the photo to create the comment on.
            body (CommentSchema): The schema containing the data to be used in creating a new Comment object.
            created_by (User, optional): A User object representing who is creating this comment. Defaults to Depends(get_current_user).
            db (AsyncSession, optional): An AsyncSession instance that can be used for database operations within this function call only. Defaults to Depends(get_db).
    
    :param photo_id: int: Specify the photo that the comment is being created for
    :param body: CommentSchema: Validate the data sent in the request body
    :param created_by: User: Get the user that is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A CommentResponse object
    """
    if body.comment.strip():
        comment = await repository_comments.create_comment(body, photo_id, created_by.id, db)
        return CommentResponse(comment_id=comment.id,
                               comment=comment.comment,
                               created_at= comment.created_at,
                               photo_id= comment.photo_id,
                               created_by= comment.created_by)
    else:
        raise HTTPException(status_code=400, detail="Comment can not be blank")
    


@router.get('/{photo_id}/comments', response_model=list[CommentResponse])
async def get_comments(photo_id: int, 
                      limit: int = Query(10, ge=10, le=500), 
                      offset: int = Query(0, ge=0), 
                      db: AsyncSession = Depends(get_db)):
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
    result = []
    for comment in comments:
        result.append(CommentResponse(comment_id=comment.id,
        comment=comment.comment,
        created_at= comment.created_at,
        photo_id= comment.photo_id,
        created_by= comment.created_by))
    return result


@router.put('/{photo_id}/comments')
async def update_comment(comment_id: int, 
                         body:CommentSchema, 
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    comment = await repository_comments.update_comment(comment_id, body, user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return CommentResponse(comment_id=comment.id,
        comment=comment.comment,
        created_at= comment.created_at,
        photo_id= comment.photo_id,
        created_by= comment.created_by)


# @router.delete('/{photo_id}/comments', status_code=status.HTTP_204_NO_CONTENT)
# async def delete_contact(contact_id: int, 
#                          db: AsyncSession = Depends(get_db),
#                          user: User = Depends(get_current_user)):
#     contact = await repository_comments.delete_contact(contact_id, db, user)
#     return contact


    