from __future__ import annotations

from typing import Optional, Type

import redis
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.security import (
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository.users import get_current_user
from src.schemas import RateModelResponse, RateModel, ListRatesModelResponse
from src.security.role_permissions import RoleChecker
from src.repository import (
    rates as repository_rates,
    photos as repository_photos
)
from src.conf.config import settings


router = APIRouter(prefix="/rates", tags=["rates"])
security = HTTPBearer()


@router.get(
        "/",
        response_model=Optional[ListRatesModelResponse]
)
async def get_rates_by_user(
    list_user_id: Optional[list[int]] = Query(None),
    db: Session = Depends(RoleChecker(allowed_roles=["admin", "moderator"]))
):
    """
    Retrieves rates based on user identifiers.

    :param list_user_id: List of user identifiers for filtering rates.
    :type list_user_id: Optional[list[int]]
    :param db: The database session object.
    :type db: Session
    :return: Dictionary containing rates filtered by user identifiers.
    :rtype: dict
    """
    rates = []

    if list_user_id:
        
        for user_id in list_user_id:
            if user_id != 0:
                rates.extend(await repository_rates.get_rates(db = db, **{"created_by": user_id}))
        
        return {"rates": rates}

    rates = await repository_rates.get_rates(db = db)
    return {"rates": rates}
    

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


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_rates_of_photo(
    user_id: int,
    list_rate_id: Optional[list[int]] = Query(None),
    db: Session = Depends(RoleChecker(allowed_roles=["admin", "moderator"]))
):
    """
    Deletes rates associated with a user for a photo.

    :param user_id: The identifier of the user whose rates are to be deleted.
    :type user_id: int
    :param list_rate_id: List of rate identifiers for filtering and delete.
    :type list_rate_id: Optional[list[int]]
    :param db: The database session object.
    :type db: Session
    """
    rates = []

    if list_rate_id:
        
        for rate_id in list_rate_id:
            if rate_id != 0:
                rates.extend(await repository_rates.get_rates(db = db, **{"id": rate_id, "created_by": user_id}))
    else:
        rates = await repository_rates.get_rates(db = db, **{"created_by": user_id})
    
    await repository_rates.delete_rates(rates = rates, db = db)
