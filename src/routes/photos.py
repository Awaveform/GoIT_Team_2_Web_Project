from __future__ import annotations


from fastapi import UploadFile, File, status, HTTPException, Query
from fastapi.openapi.models import Response

from redis.asyncio import Redis
from typing import Optional, List, Union, Dict
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPBearer,
)

from src.cache.async_redis import get_redis
from src.database.models.user import User
from src.enums import Roles
from src.repository import users as repository_users
from src.repository import photos as repository_photos
from src.database.db import get_db
from src.repository.users import get_current_user
from src.schemas import PhotoResponseWithTags
from src.schemas import PhotoResponse, PhotoUpdate
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()


@router.get("/", response_model=Dict[str, Union[List[PhotoResponse], PhotoResponse]])
async def get_photos(
    db: Session = Depends(get_db),
    r: Redis = Depends(get_redis),
    user_id: Optional[int] = None,
    photo_id: Optional[int] = None,
    limit: int = Query(10, gt=0, le=1000),
    skip: int = Query(0, ge=0),
):
    """
    Retrieve photos from the database.

    :param db: Session: Database session.
    :type db: Session
    :param r: Redis: Redis connection.
    :type r: Redis
    :param user_id: Optional[int]: User ID to filter photos by user.
    :type user_id: Optional[int]
    :param photo_id: Optional[int]: Photo ID to retrieve a specific photo.
    :type photo_id: Optional[int]
    :param limit: int: Maximum number of photos to retrieve (default: 10, maximum: 1000).
    :type limit: int
    :param skip: int: Number of records to skip before starting to return photos.
    :type skip: int
    :return: Dictionary containing a list of photos or a single photo.
    :rtype: Dict[str, Union[List[PhotoResponse], PhotoResponse]]
    """
    if user_id is not None:
        user_exists = await repository_users.get_user_by_user_id(user_id, db, r)
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} was not found.",
            )

    photos = await repository_photos.find_photos(
        db=db,
        photo_id=photo_id,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )

    if not photos:
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content={"message": "No content"}
        )

    return {"photos": photos}


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(repository_users.get_current_user),
    file: UploadFile = File(),
):
    """
    Create a new photo.

    :param description: Optional[str]: Description of the photo.
    :type description: Optional[str]
    :param db: Session: Database session.
    :type db: Session
    :param current_user: User: Current authenticated user.
    :type current_user: User
    :param file: UploadFile: Image file to upload.
    :type file: UploadFile
    :return: PhotoResponse: Response containing the created photo information.
    :rtype: PhotoResponse
    """
    new_photo = await repository_photos.create_photo(
        description=description, current_user=current_user, db=db, file=file
    )

    return PhotoResponse(
        id=new_photo.id,
        url=new_photo.url,
        description=new_photo.description,
        created_by=new_photo.created_by,
        created_at=new_photo.created_at,
    )


@router.delete("/{photo_id}", response_model=PhotoResponse)
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(repository_users.get_current_user),
    r: Redis = Depends(get_redis),
):
    """
    Delete a photo.

    :param photo_id: int: ID of the photo to delete.
    :type photo_id: int
    :param db: Session: Database session.
    :type db: Session
    :param current_user: User: Current authenticated user.
    :type current_user: User
    :param r: Redis: Redis connection.
    :type r: Redis
    :return: PhotoResponse: Response containing the deleted photo information.
    :rtype: PhotoResponse
    """
    current_user_role = await repository_users.get_user_role(
        user_id=current_user.id, db=db, r=r
    )

    photo = await repository_photos.get_photo_by_photo_id(photo_id=photo_id, db=db)

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    if (
        current_user_role.name == Roles.ADMIN.value
        or photo.created_by == current_user.id
    ):
        deleted_photo = await repository_photos.delete_photo(photo=photo, db=db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden, only the owner or admin can delete the photo",
        )

    return PhotoResponse(
        id=deleted_photo.id,
        url=deleted_photo.url,
        description=deleted_photo.description,
        created_by=deleted_photo.created_by,
        created_at=deleted_photo.created_at,
    )


@router.post("/photos/{photo_id}/tags", response_model=PhotoResponseWithTags)
async def add_tags(
    photo_id: int,
    tag_names: Optional[list[str]] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add tags to a photo.

    :param photo_id: int: ID of the photo.
    :type photo_id: int
    :param tag_names: Optional[list[str]]: List of tag names to add.
    :type tag_names: Optional[list[str]]
    :param current_user: User: Current authenticated user.
    :type current_user: User
    :param db: Session: Database session.
    :type db: Session
    :return: PhotoResponseWithTags: Response containing the updated photo information with tags.
    :rtype: PhotoResponseWithTags
    """
    if not tag_names:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    photo = await repository_photos.get_photo_by_photo_id(photo_id=photo_id, db=db)
    if not photo:
        raise HTTPException(
            status_code=404, detail=f"Photo with photo_id- {photo_id} not found."
        )

    if current_user.id != photo.created_by:
        raise HTTPException(
            status_code=403,
            detail="Forbidden, only the owner can add tags to the photo.",
        )

    existing_photo_tags = await repository_photos.get_tags_by_photo_id(
        photo.id,
        db,
    )
    photo_tag_names = [tag.name for tag in existing_photo_tags]

    if len(existing_photo_tags) + len(tag_names) > 5:
        raise HTTPException(
            status_code=400,
            detail="The number of tags cannot exceed 5",
        )

    for tag_name in tag_names:
        if tag_name not in photo_tag_names:
            tag = await repository_photos.add_tag_by_name(
                tag_name=tag_name, current_user=current_user, db=db
            )
            photo = await repository_photos.add_tags_to_photo(
                photo=photo, tag=tag, db=db
            )
    return photo


@router.put("/photos/{photo_id}/description", response_model=PhotoUpdate)
async def update_photo_description(
    photo_id: int,
    new_description: Optional[str] = "",
    current_user: User = Depends(repository_users.get_current_user),
    db: Session = Depends(get_db),
    r: Redis = Depends(get_redis),
):
    """
    Update the description of a photo.

    :param photo_id: int: ID of the photo.
    :type photo_id: int
    :param new_description: Optional[str]: New description for the photo.
    :type new_description: Optional[str]
    :param current_user: User: Current authenticated user.
    :type current_user: User
    :param db: Session: Database session.
    :type db: Session
    :param r: Redis: Redis connection.
    :type r: Redis
    :return: PhotoUpdate: Response containing the updated photo information.
    :rtype: PhotoUpdate
    """
    if not new_description.strip():
        raise HTTPException(
            status_code=400, detail="Bad request. Description can not be empty."
        )

    current_user_role = await repository_users.get_user_role(
        user_id=current_user.id, db=db, r=r
    )

    photo = await repository_photos.get_photo_by_photo_id(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if photo.created_by == current_user.id or current_user_role.name in {
        Roles.ADMIN.value,
        Roles.MODERATOR.value,
    }:
        updated_photo = await repository_photos.update_photo_description(
            photo, new_description, db
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden, only the owner, admin or moderator can "
            "updating photo description.",
        )
    return PhotoUpdate(
        id=updated_photo.id,
        description=updated_photo.description,
        created_by=updated_photo.created_by,
        created_at=updated_photo.created_at,
        updated_at=updated_photo.updated_at,
        url=updated_photo.url,
    )
