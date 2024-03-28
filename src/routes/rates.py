from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.security import (
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.schemas import ListRatesModelResponse
from src.security.role_permissions import RoleChecker
from src.repository import (
    rates as repository_rates,
)


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
