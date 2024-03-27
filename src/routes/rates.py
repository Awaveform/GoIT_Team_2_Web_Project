from __future__ import annotations

from typing import Optional, Type

import redis
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import (
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository.users import get_current_user
from src.schemas import RateModelResponse, RateModel
from src.repository import (
    rates as repository_rates,
    photos as repository_photos
)
from src.conf.config import settings


router = APIRouter(prefix="/rates", tags=["rates"])
security = HTTPBearer()


@router.post(
    "/{photo_id}",
    response_model=Optional[RateModelResponse],
    status_code=status.HTTP_201_CREATED
)
async def create_rates_for_photo(
    photo_id: int,
    grade: RateModel,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a rate for a photo.

    :param photo_id: The identifier of the photo for which the rate is created.
    :type photo_id: int
    :param grade: The rate given to the photo.
    :type grade: RateModel
    :param user: The current authenticated user.
    :type user: User
    :param db: The database session object.
    :type db: Session
    :return: The created rate object.
    :rtype: Rate
    """
    if grade.grade < 1 or grade.grade > 5:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "The grade must be greater than 1 and less than or equal to 5."
        )

    photos = await repository_photos.get_photos_by_user_id(
        user_id = user.id,
        db = db
    )
    photo = [photo for photo in photos if photo.id == photo_id]
    
    if photo:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Owner of a photo has not availability to rate the photo."
        )
    
    rates = await repository_rates.get_rates(
        db = db,
        created_by = user.id,
        photo_id = photo_id
    )

    if rates:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Rate can be added to a photo only once"
        )

    rate = await repository_rates.create_rate_photo(
        photo_id = photo_id,
        grade = grade.grade,
        user_id = user.id,
        db = db
    )

    return rate
