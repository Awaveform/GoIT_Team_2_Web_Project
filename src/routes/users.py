from __future__ import annotations

from fastapi import HTTPException
from typing import Optional, Type, Coroutine, Any

from fastapi import APIRouter, Depends, status
from fastapi.security import (
    HTTPBearer,
)
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from src.cache.async_redis import get_redis
from src.database.db import get_db
from src.database.models.role import Role
from src.database.models.user import User
from src.enums import Roles
from src.schemas import UserDetailedResponse, UserResponse
from src.repository import users as repository_users
from src.security.role_permissions import RoleChecker

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


@router.patch(
    "/block/{user_id}",
    response_model=Optional[UserResponse],
)
async def block_user(
    user_id: int,
    db: Session = Depends(RoleChecker(allowed_roles=[Roles.ADMIN.value])),
    r: Redis = Depends(get_redis),
):
    """
    Method that blocks user with a specific user_id.
    :param r: Redis instance.
    :type r: redis.asyncio.Redis.
    :param user_id: User's identifier.
    :type user_id: int.
    :param db: DB session object.
    :type db: Session.
    :return: User info.
    :rtype: UserResponse.
    """
    user: Coroutine[
        Any, Any, Type[User] | bool
    ] = await repository_users.get_user_by_user_id(user_id=user_id, db=db, r=r)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the user identifier {user_id} is not found",
        )
    user = await repository_users.block_user(user, db=db)
    role: Type[Role] = await repository_users.get_user_role(user_id=user.id, db=db, r=r)
    return UserResponse(
        id=user.id,
        is_active=user.is_active,
        role=role.name,
        first_name=user.first_name,
        last_name=user.last_name,
        user_name=user.user_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
