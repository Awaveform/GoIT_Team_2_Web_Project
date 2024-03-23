from typing import Optional

import redis
from fastapi import Header, UploadFile, File
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import (
    HTTPBearer,
)
from fastapi_jwt_auth import AuthJWT
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import and_
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository.users import get_current_user, get_user_by_user_name
from src.schemas import UserModel, UserResponse, TokenModelResponse, TokenModel, \
    UserDetailedResponse, Roles
from src.repository import users as repository_users
from src.services.auth import get_password_hash, verify_password
from src.conf.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
r = redis.Redis(host=settings.redis_host, port=settings.redis_port)

@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    body: UserModel,
    db: Session = Depends(get_db),
):
    """
    The signup function creates a new user in the database.
    It takes a UserModel object as input, which is validated by pydantic.
    If the email address already exists in the database, it raises an HTTP 409 error.
    Otherwise, it hashes and salts the password using passlib's get_password_hash
    function and then adds that to body before creating a new user with repository_users'
    create_user function.

    :param body: Get the user's information from the request body
    :type body: UserModel
    :param db: Access the database
    :type db: Session.
    :return: A dict with the user and a message
    :rtype: UserResponse.
    """
    exist_user = await repository_users.get_user_by_user_name(body.user_name, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with the user_name {body.user_name} already exists",
        )
    body.password = get_password_hash(body.password)
    default_role: Roles = Roles.USER
    new_user, new_user_role = await repository_users.create_user(body, default_role, db)
    return UserResponse(
        id=new_user.id,
        is_active=new_user.is_active,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        user_name=new_user.user_name,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        role=default_role.value
    )

@router.post(
    "/login",
    response_model=Optional[TokenModelResponse],
)
async def create_session(
    user: TokenModel, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)
):
    """
    The create_session function creates a new session for the user.

    :param user: Pass the user object to the function.
    :type user: TokenModel.
    :param Authorize: Create the access token and refresh token.
    :type Authorize: AuthJWT.
    :param db: Access the database.
    :type db: Session.
    :return: A dictionary with three keys: access_token, refresh_token and token_type
    :rtype: TokenModelResponse.
    """
    _user = await repository_users.get_user_by_user_name(user.user_name, db)
    if _user:
        if not verify_password(user.password, _user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
            )
        access_token = Authorize.create_access_token(subject=_user.user_name)
        refresh_token = Authorize.create_refresh_token(subject=_user.user_name)

        _user.refresh_token = refresh_token
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    raise HTTPException(status_code=401, detail="Invalid user name")

@router.get(
    "/refresh_token",
    response_model=TokenModel,
)
async def refresh_token(
    refresh_token: str = Header(..., alias="Authorization"),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh_token as an argument and returns a new
        access_token and refresh_token.
        The function also updates the user's current refresh token with a new one.

    :param refresh_token: Pass the refresh token from the request header.
    :type refresh_token: str.
    :param Authorize: Check if the user is authorized to access the endpoint.
    :type Authorize: AuthJWT.
    :param db: Access the database.
    :type db: Session.
    :return: A new access token and a new refresh token.
    :rtype: TokenModel.
    """
    Authorize.jwt_refresh_token_required()
    # Check if refresh token is in DB
    user_name = Authorize.get_jwt_subject()
    user = db.query(User).filter(and_(user_name == User.email)).first()
    if f"Bearer {user.refresh_token}" == refresh_token:
        access_token = Authorize.create_access_token(subject=user_name)
        new_refresh_token = Authorize.create_refresh_token(subject=user_name)

        user.refresh_token = new_refresh_token
        db.commit()
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
