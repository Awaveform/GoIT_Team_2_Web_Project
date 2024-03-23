from __future__ import annotations

import pickle
from functools import wraps
from typing import Type, Tuple, List

import redis
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User, UserRole, Role, Photo
from src.repository.photos import get_photos_by_user_id
from src.schemas import UserModel, UserRoleModel, Roles

r = redis.Redis(host=settings.redis_host, port=settings.redis_port)


async def get_role(_role: Roles, db: Session) -> Type[Role]:
    """
    Method that gets information about role.

    :param _role: Role name.
    :type _role: Roles.
    :param db: DB session object.
    :type db: Session.
    :return: Full role info.
    :rtype: Role.
    """
    role = r.get(f"role:{_role}")
    if role is None:
        role = db.query(Role).filter(Role.name == _role.value).first()
        r.set(f"role:{_role}", pickle.dumps(role))
        r.expire(f"roles", 1900)
    else:
        role = pickle.loads(role)
    return role


async def get_user_role(user_id: int, db: Session = Depends(get_db)) -> Type[Role]:
    """
    Method that gets information about the user role.

    :param user_id: User identifier.
    :type user_id: int.
    :param db: DB session object.
    :type db: Session.
    :return: Role assigned to the user.
    :rtype: Role.
    """
    role = r.get(f"user_role:{user_id}")
    if role is None:
        role = db.query(Role).join(UserRole, Role.id == UserRole.role_id).filter(
            UserRole.user_id == user_id).first()
        r.set(f"user_role:{user_id}", pickle.dumps(role))
        r.expire(f"user_role:{user_id}", 1900)
    else:
        role = pickle.loads(role)
    return role


async def assign_role_to_user(user_id: int, role: Type[Role], db: Session) -> UserRole:
    """
    Method that assigns a role to the user.

    :param user_id: User identifier.
    :type user_id: int.
    :param role: Role info.
    :type role: Type[Role].
    :param db: DB session object.
    :type db: Session.
    :return: User role info.
    :rtype: UserRole.
    """
    user_role_data = {"user_id": user_id, "role_id": role.id}
    new_user_role = UserRole(**user_role_data)
    db.add(new_user_role)
    db.commit()
    return new_user_role


async def get_user_by_user_name(user_name: str, db: Session) -> Type[User] | bool:
    """
    The get_user_by_email function takes in an email and a database session.
    It then checks the Redis cache for a user with that email, if it finds one, it
    returns the user object.
    If not, it queries the database for that user and stores them in Redis before
    returning them.

    :param user_name: Get the user by user_name.
    :type user_name: str.
    :param db: Connect to the database.
    :type db: Session.
    :return: A user object if the user_name exists in the database.
    :rtype: Type[User] | bool.
    """
    current_user = r.get(f"user:{user_name}")
    if current_user is None:
        current_user = db.query(User).filter(User.user_name == user_name).first()
        if current_user is None:
            return False
        r.set(f"user:{user_name}", pickle.dumps(current_user))
        r.expire(f"user:{user_name}", 900)
    else:
        current_user = pickle.loads(current_user)
    return current_user


async def create_user(body: UserModel, role: Roles, db: Session) -> Tuple[User, UserRole]:
    """
    The create_user function creates a new user in the database.

    :param role: Role name.
    :type role: Roles.
    :param body: Create a new user object.
    :type body: UserModel.
    :param db: Pass the database session to the function.
    :type db: Session.
    :return: A user object.
    :rtype: User.
    """
    body_dict: dict = body.dict()
    role: Type[Role] = await get_role(_role=role, db=db)
    new_user = User(**body_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    new_user_role = await assign_role_to_user(role=role, user_id=new_user.id, db=db)
    return new_user, new_user_role


async def get_full_user_info_by_name(user_name: str, db: Session) -> Tuple[User, int]:
    """
    Method that gets information about user.

    :param user_name: User name.
    :type user_name: str.
    :param db: DB session object.
    :type db: Session.
    :return: Info about user.
    :rtype: User.
    """
    user: User | bool = await get_user_by_user_name(user_name=user_name, db=db)
    photos: list[Type[Photo]] = await get_photos_by_user_id(user_id=user.id, db=db)
    return user, len(photos)


async def assign_user_role(body: UserRoleModel, db: Session) -> UserRole:
    """
    The assign_user_role function assigns a role to the user in the database.

    :param body: Create a new user role object.
    :type body: UserRoleModel.
    :param db: Pass the database session to the function.
    :type db: Session.
    :return: A user role object.
    :rtype: UserRole.
    """
    new_user_role = UserRole(**body.dict())
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    return new_user_role


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: Identify the user that is being updated.
    :type user: User.
    :param token: Update the refresh token in the database.
    :type token: str | None.
    :param db: Pass the database session to the function.
    :type db: Session.
    :return: None.
    :rtype: None.
    """
    user.refresh_token = token
    db.commit()


async def get_current_user(
    Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)
) -> Type[User]:
    """
    The get_current_user function is a dependency that can be used to get the current
    user.
    It will use the JWT token in the Authorization header to retrieve and return a User
    object.

    :param Authorize: Get the current user's email.
    :type Authorize: AuthJWT.
    :param db: Get the database session.
    :type db: Session.
    :return: The current user.
    :rtype: Type[User].
    """
    Authorize.jwt_required()

    user_name = Authorize.get_jwt_subject()

    return await get_user_by_user_name(user_name, db)
