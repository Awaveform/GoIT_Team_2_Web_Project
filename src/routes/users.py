from __future__ import annotations

from typing import Optional, Type

import redis
from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository.users import get_current_user, check_user_role, allowed_roles
from src.schemas import UserDetailedResponse, Roles
from src.repository import users as repository_users
from src.conf.config import settings


router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()
r = redis.Redis(host=settings.redis_host, port=settings.redis_port)


@router.get(
    "/{user_name}",
    response_model=Optional[UserDetailedResponse],
)
@allowed_roles(["admin"])
async def get_user_info(
    user_name: str,
    db: Session = Depends(get_db),
):
    """
    Method that returns the full user info for the specific user.
    :param check_role: Check user role.
    :type check_role: bool.
    :param user_name: User name.
    :type user_name: str.
    :param db: DB session object.
    :type db: Session.
    :return: Detailed user info.
    :rtype: UserDetailedResponse.
    """
    user, uploaded_photos = await repository_users.get_full_user_info_by_name(
        user_name=user_name, db=db
    )
    role: Type[Role] = await repository_users.get_user_role(user_id=user.id)
    return UserDetailedResponse(
        id=user.id,
        is_active=user.is_active,
        first_name=user.first_name,
        last_name=user.last_name,
        user_name=user.user_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role=role.name,
        uploaded_photos=uploaded_photos,
    )
