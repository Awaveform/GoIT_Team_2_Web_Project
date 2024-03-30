from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.security import (
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import (
    photos as repository_photos,
    rates as repository_rates
)
from src.repository.users import get_current_user
from src.schemas import ListRatesModelResponse, RateModel, RateModelResponse
from src.security.role_permissions import RoleChecker


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
                rates.extend(await repository_rates.get_rates(db=db, created_by=user_id))
        
        return {"rates": rates}

    rates = await repository_rates.get_rates(db=db)
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
    photo = await repository_photos.get_photo_by_photo_id(
        photo_id=photo_id,
        db=db
    )

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The photo {photo_id} does not exist."
        )

    if photo.created_by == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner of a photo has not availability to rate the photo."
        )
    
    rates = await repository_rates.get_rates(
        db=db,
        created_by=user.id,
        photo_id=photo_id
    )

    if rates:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rate can be added to a photo only once"
        )

    rate = await repository_rates.create_rate_photo(
        photo_id=photo_id,
        grade=grade.grade,
        user_id=user.id,
        db=db
    )

    return rate
