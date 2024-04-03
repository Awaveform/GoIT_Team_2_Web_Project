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


@router.put("/photos/{photo_id}/description", response_model=PhotoUpdate)
async def update_photo_description(
        photo_id: int,
        new_description: Optional[str] = None,
        current_user: User = Depends(repository_users.get_current_user),
        db: Session = Depends(get_db),
        r: Redis = Depends(get_redis)):

    current_user_role = await repository_users.get_user_role(
        user_id=current_user.id, db=db, r=r)

    photo = await repository_photos.get_photo_by_photo_id(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if current_user_role.name == 'admin' or photo.created_by == current_user.id or current_user_role.name == 'moderator':
        updated_photo = await repository_photos.update_photo_description(photo, new_description, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden, only the owner, admin or moderator can updating photo description")
    return PhotoUpdate(
        id=updated_photo.id,
        description=updated_photo.description,
        created_by=updated_photo.created_by,
        created_at=updated_photo.created_at,
        updated_at=updated_photo.updated_at,
        url=updated_photo.url
    )



