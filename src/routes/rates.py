from __future__ import annotations

from typing import Optional

from redis.asyncio import Redis
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.security import (
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.cache.async_redis import get_redis
from src.database.db import get_db
from src.database.models.user import User
from src.enums import Roles
from src.schemas import (
    RateModelResponse,
    RateModel,
    ListRatesModelResponse,
    DeleteRatesResponse,
)
from src.repository import (
    users as repository_users,
    photos as repository_photos,
    rates as repository_rates,
)
from src.security.role_permissions import RoleChecker


router = APIRouter(prefix="/rates", tags=["rates"])
security = HTTPBearer()


@router.get("/", response_model=Optional[ListRatesModelResponse])
async def get_rates_by_user(
    list_user_id: Optional[list[int]] = Query(None),
    db: Session = Depends(
        RoleChecker(allowed_roles=[Roles.ADMIN.value, Roles.MODERATOR.value])
    ),
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
    if list_user_id:
        rates = await repository_rates.get_rates(db=db, created_by=list_user_id)
    else:
        rates = await repository_rates.get_rates(db=db)
    return {"rates": rates}


@router.post(
    "/{photo_id}",
    response_model=Optional[RateModelResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_rates_for_photo(
    photo_id: int,
    grade: RateModel,
    user: User = Depends(repository_users.get_current_user),
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
    photo = await repository_photos.get_photo_by_photo_id(photo_id=photo_id, db=db)

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The photo {photo_id} does not exist.",
        )

    if photo.created_by == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner of a photo has not availability to rate the photo.",
        )

    rates = await repository_rates.get_rates(
        db=db, created_by=user.id, photo_id=photo_id
    )

    if rates:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rate can be added to a photo only once",
        )

    rate = await repository_rates.create_rate_photo(
        photo_id=photo_id, grade=grade.grade, user_id=user.id, db=db
    )

    return rate


@router.delete("/{user_id}", response_model=Optional[DeleteRatesResponse])
async def delete_rates_of_photo(
    user_id: int,
    list_rate_id: Optional[list[int]] = Query(None),
    db: Session = Depends(
        RoleChecker(allowed_roles=[Roles.ADMIN.value, Roles.MODERATOR.value])
    ),
    r: Redis = Depends(get_redis),
):
    """
    Deletes rates associated with a user for a photo.

    :param user_id: The identifier of the user whose rates are to be deleted.
    :type user_id: int
    :param list_rate_id: List of rate identifiers to be deleted.
    :type list_rate_id: Optional[list[int]]
    :param db: The database session object.
    :type db: Session
    :param r: The Redis client.
    :type r: Redis
    :return: A dictionary containing a message detailing the result of the operation.
    :rtype: dict
    """
    user = await repository_users.get_user_by_user_id(user_id=user_id, db=db, r=r)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' does not exist.",
        )

    deleted_rates = []
    undeleted_rates = []

    if list_rate_id:
        for rate_id in list_rate_id:
            rates = await repository_rates.get_rates(
                db=db, id=rate_id, created_by=user_id
            )
            if rates:
                deleted_rates.append(rate_id)
            else:
                undeleted_rates.append(rate_id)

        if undeleted_rates and deleted_rates:
            detail = f"Rates of user with id '{user_id}': deleted ids {deleted_rates}, don't exist ids {undeleted_rates}."
        elif not deleted_rates:
            detail = (
                f"Rates of user with id '{user_id}': don't exist ids {undeleted_rates}."
            )
        else:
            detail = f"Rates of user with id '{user_id}': deleted ids {deleted_rates}."
    else:
        deleted_rates = [
            rate.id
            for rate in await repository_rates.get_rates(db=db, created_by=user_id)
        ]
        detail = f"All user's rates with id '{user_id}' have been successfully deleted."

    if deleted_rates:
        await repository_rates.delete_rates(rates_id=deleted_rates, db=db)
    return {"detail": detail}
