from __future__ import annotations

from typing import Optional, Type

from fastapi import APIRouter, Depends
from fastapi.security import (
    HTTPBearer,
)
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from src.cache.async_redis import get_redis
from src.database.db import get_db
from src.database.models.role import Role
from src.schemas import UserDetailedResponse
from src.repository import users as repository_users

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()


@router.get(
    "/{user_name}",
    response_model=Optional[UserDetailedResponse],
)
async def get_user_info(
    user_name: str, db: Session = Depends(get_db), r: Redis = Depends(get_redis)
):
    """
    Method that returns the full user info for the specific user.
    :param r: Redis instance.
    :type r: redis.asyncio.Redis.
    :param user_name: User's name.
    :type user_name: str.
    :param db: DB session object.
    :type db: Session.
    :return: Detailed user info.
    :rtype: UserDetailedResponse.
    """
    user, uploaded_photos = await repository_users.get_full_user_info_by_name(
        user_name=user_name, db=db, r=r
    )
    role: Type[Role] = await repository_users.get_user_role(user_id=user.id, db=db, r=r)
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
