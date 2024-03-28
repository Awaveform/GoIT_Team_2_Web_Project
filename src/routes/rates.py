from __future__ import annotations

from typing import Optional, Type

from fastapi import APIRouter, Depends, Query
from fastapi.security import (
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.models import Rate
from src.security.role_permissions import RoleChecker
from src.schemas import DeleteRatesResponse
from src.repository import (
    rates as repository_rates
)


router = APIRouter(prefix="/rates", tags=["rates"])
security = HTTPBearer()


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
    rates: list[Type[Rate]] | None = []

    if list_rate_id:
        
        for rate_id in list_rate_id:
            if rate_id != 0:
                rates.extend(await repository_rates.get_rates(db=db, **{"id": rate_id, "created_by": user_id}))
        detail = f"Rates {[rate.id for rate in rates]} of user {user_id} have been successfully deleted."
    else:
        rates = await repository_rates.get_rates(db=db, **{"created_by": user_id})
        detail = f"All user {user_id} rates have been successfully deleted."
    
    await repository_rates.delete_rates(rates=rates, db=db)
    return {"detail": detail}
