from __future__ import annotations

from typing import Optional, Type

from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.security import (
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Rate
from src.security.role_permissions import RoleChecker
from src.repository.users import get_current_user
from src.schemas import RateModelResponse, RateModel, DeleteRatesResponse
from src.repository import (
    rates as repository_rates,
    photos as repository_photos
)


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


@router.delete(
    "/{user_id}",
    response_model=Optional[DeleteRatesResponse]
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
    rates: list[Type[Rate]] = []

    if list_rate_id:
        
        for rate_id in list_rate_id:
            if rate_id != 0:
                rates.extend(await repository_rates.get_rates(db=db, id=rate_id, created_by=user_id))
        detail = f"Rates {[rate.id for rate in rates]} of user {user_id} have been successfully deleted."
    else:
        rates = await repository_rates.get_rates(db=db, created_by=user_id)
        detail = f"All user {user_id} rates have been successfully deleted."
    
    await repository_rates.delete_rates(rates=rates, db=db)
    return {"detail": detail}