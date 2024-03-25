from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import UserRole
from src.repository.users import get_current_user


class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    async def __call__(self, auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
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
        user = await get_current_user(auth)
        user_role = (
            db.query(UserRole)
            .filter(UserRole.user_id == user.id)
            .first()
        )
        if user_role and user_role.role.name not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have enough permissions"
            )
        return db
