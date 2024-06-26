from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from src.cache.async_redis import get_redis
from src.database.db import get_db
from src.database.models.user_role import UserRole
from src.repository.users import get_current_user


class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        auth: AuthJWT = Depends(),
        db: Session = Depends(get_db),
        r: Redis = Depends(get_redis),
    ):
        """
        Dependency function that checks the user's role and returns the DB
        session object.
        If the user's role is not allowed, it raises an HTTPException.

        :param auth: AuthJWT instance.
        :type auth: AuthJWT.
        :param db: DB session object.
        :type db: Session.
        :return: DB session object.
        :rtype: Session.
        """
        user = await get_current_user(auth, db, r)
        user_role = db.query(UserRole).filter(UserRole.user_id == user.id).first()
        if not user_role or user_role.role.name not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions",
            )
        return db
