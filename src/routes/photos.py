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
from src.database.models import User
from src.repository import users as repository_users
from src.repository import photos as repository_photos
from src.database.db import get_db
from src.schemas import PhotoResponse, PhotoResponseWithTags
from src.schemas import PhotoResponse, PhotoUpdate
from src.schemas import PhotoResponse, PhotoUpdate

router = APIRouter(prefix="/photos", tags=["photos"])
security = HTTPBearer()


@router.get(
    "/",
    response_model=Dict[str, Union[List[PhotoResponse], PhotoResponse]]
)
async def get_photos(
        db: Session = Depends(get_db),
        r: Redis = Depends(get_redis),
        user_id: Optional[int] = None,
        photo_id: Optional[int] = None,
        limit: int = Query(10, gt=0, le=1000),
        skip: int = Query(0, ge=0)):

    if user_id is not None:
        user_exists = await repository_users.get_user_by_user_id(
            user_id, db, r
        )
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} was not found."
            )

    photos = await repository_photos.find_photos(
        db=db,
        photo_id=photo_id,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )

    if not photos:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return {"photos": photos}


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_photo(description: Optional[str] = None, db: Session = Depends(get_db),
                       current_user: User = Depends(repository_users.get_current_user),
                       file: UploadFile = File()):
    new_photo = await repository_photos.create_photo(
        description=description,
        current_user=current_user,
        db=db,
        file=file)

    return PhotoResponse(
        id=new_photo.id,
        url=new_photo.url,
        description=new_photo.description,
        created_by=new_photo.created_by,
        created_at=new_photo.created_at,
    )


@router.delete("/{photo_id}", response_model=PhotoResponse)
async def delete_photo(photo_id: int,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(repository_users.get_current_user),
                       r: Redis = Depends(get_redis)):

    current_user_role = await repository_users.get_user_role(
        user_id=current_user.id, db=db, r=r)

    photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id,
        db=db
        )

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found")

    if current_user_role.name == 'admin' or photo.created_by == current_user.id:
        deleted_photo = await repository_photos.delete_photo(
            photo=photo, db=db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden, only the owner or admin can delete the photo")

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
        current_user: User = Depends(repository_users.get_current_user),
        db: Session = Depends(get_db)):

    # Перевірка, що фотографія існує
    photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id,
        db=db
    )
    if not photo:
        raise HTTPException(status_code=404, detail=f"Photo with photo_id- {photo_id} not found")

    if current_user.id != photo.created_by:
        raise HTTPException(status_code=403, detail="Forbidden, only the owner can add tags to the photo")

    # Отримання списку тегів на фотографії
    existing_tags = await repository_photos.get_tags_by_photo_id(photo.id, db)
    existing_tag_names = [tag.name for tag in existing_tags]

    # Перевірка, що кількість тегів не перевищує 5
    if len(existing_tags) + len(tag_names) > 5:
        raise HTTPException(status_code=400, detail="The number of tags cannot exceed 5")

    for tag_name in tag_names:
        if tag_name not in existing_tag_names:
            tag = await repository_photos.add_tag_by_name(tag_name=tag_name, current_user=current_user, db=db)
            photo_with_tags = await repository_photos.add_tags_to_photo(photo=photo, tag=tag, db=db)
    return photo_with_tags

@router.put("/photos/{photo_id}/description", response_model=PhotoUpdate)
async def update_photo_description(
        photo_id: int,
        new_description: Optional[str] = "",
        current_user: User = Depends(repository_users.get_current_user),
        db: Session = Depends(get_db),
        r: Redis = Depends(get_redis),
):
    if not new_description.strip():
        raise HTTPException(
            status_code=400, detail="Bad request. Description can not be empty."
        )

    current_user_role = await repository_users.get_user_role(
        user_id=current_user.id, db=db, r=r)

    photo = await repository_photos.get_photo_by_photo_id(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if (
            photo.created_by == current_user.id or
            current_user_role.name in {'admin', 'moderator'}
    ):
        updated_photo = await repository_photos.update_photo_description(
            photo, new_description, db
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden, only the owner, admin or moderator can "
                   "updating photo description."
        )
    return PhotoUpdate(
        id=updated_photo.id,
        description=updated_photo.description,
        created_by=updated_photo.created_by,
        created_at=updated_photo.created_at,
        updated_at=updated_photo.updated_at,
        url=updated_photo.url
    )

@router.put("/photos/{photo_id}/description", response_model=PhotoUpdate)
async def update_photo_description(
        photo_id: int,
        new_description: Optional[str] = "",
        current_user: User = Depends(repository_users.get_current_user),
        db: Session = Depends(get_db),
        r: Redis = Depends(get_redis),
):
    if not new_description.strip():
        raise HTTPException(
            status_code=400, detail="Bad request. Description can not be empty."
        )

    current_user_role = await repository_users.get_user_role(
        user_id=current_user.id, db=db, r=r)

    photo = await repository_photos.get_photo_by_photo_id(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if (
            photo.created_by == current_user.id or
            current_user_role.name in {'admin', 'moderator'}
    ):
        updated_photo = await repository_photos.update_photo_description(
            photo, new_description, db
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden, only the owner, admin or moderator can "
                   "updating photo description."
        )
    return PhotoUpdate(
        id=updated_photo.id,
        description=updated_photo.description,
        created_by=updated_photo.created_by,
        created_at=updated_photo.created_at,
        updated_at=updated_photo.updated_at,
        url=updated_photo.url
    )



