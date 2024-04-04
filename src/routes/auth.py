from typing import Optional

from fastapi import Header
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import (
    HTTPBearer,
)
from fastapi_jwt_auth import AuthJWT
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.cache.async_redis import get_redis
from src.conf.config import settings
from src.database.db import get_db
from src.database.models.user import User
from src.schemas import UserModel, UserResponse, TokenModelResponse, TokenModel
from src.enums import Roles
from src.repository import users as repository_users
from src.services.auth import get_password_hash, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def signup(
    body: UserModel, db: Session = Depends(get_db), r: Redis = Depends(get_redis)
):
    """
    The signup function creates a new user in the database.
    It takes a UserModel object as input, which is validated by pydantic.
    If the email address already exists in the database, it raises an HTTP 409 error.
    Otherwise, it hashes and salts the password using passlib's get_password_hash
    function and then adds that to body before creating a new user with repository_users'
    create_user function.

    :param r: Redis instance.
    :type r: redis.asyncio.Redis.
    :param body: Get the user's information from the request body
    :type body: UserModel
    :param db: Access the database
    :type db: Session.
    :return: A dict with the user and a message
    :rtype: UserResponse.
    """
    exist_user = await repository_users.get_user_by_user_name(body.user_name, db, r)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with the user_name {body.user_name} already exists",
        )
    body.password = get_password_hash(body.password)
    default_role: Roles = Roles.USER
    new_user, new_user_role = await repository_users.create_user(
        body, default_role, db, r
    )
    return UserResponse(
        id=new_user.id,
        is_active=new_user.is_active,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        user_name=new_user.user_name,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        role=default_role.value,
    )


@router.post(
    "/login",
    response_model=Optional[TokenModelResponse],
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def create_session(
    user: TokenModel,
    authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
    r: Redis = Depends(get_redis),
):
    """
    The create_session function creates a new session for the user.

    :param r: Redis instance.
    :type r: redis.asyncio.Redis.
    :param user: Pass the user object to the function.
    :type user: TokenModel.
    :param authorize: Create the access token and refresh token.
    :type authorize: AuthJWT.
    :param db: Access the database.
    :type db: Session.
    :return: A dictionary with three keys: access_token, refresh_token and token_type
    :rtype: TokenModelResponse.
    """
    _user = await repository_users.get_user_by_user_name(user.user_name, db, r)
    if _user:
        if not verify_password(user.password, _user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
            )
        access_token = authorize.create_access_token(subject=_user.user_name)
        refresh_token = authorize.create_refresh_token(subject=_user.user_name)

        _user.refresh_token = refresh_token
        db.add(_user)
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    raise HTTPException(status_code=401, detail="Invalid user name")


@router.get(
    "/refresh_token",
    response_model=TokenModelResponse,
    description=f"No more than {settings.rate_limit_requests_per_minute} requests per minute",
    dependencies=[
        Depends(RateLimiter(times=settings.rate_limit_requests_per_minute, seconds=60))
    ],
)
async def refresh_token(
    refresh_token: str = Header(..., alias="Authorization"),
    authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh_token as an argument and returns a new
        access_token and refresh_token.
        The function also updates the user's current refresh token with a new one.

    :param refresh_token: Pass the refresh token from the request header.
    :type refresh_token: str.
    :param authorize: Check if the user is authorized to access the endpoint.
    :type authorize: AuthJWT.
    :param db: Access the database.
    :type db: Session.
    :return: A new access token and a new refresh token.
    :rtype: TokenModel.
    """
    authorize.jwt_refresh_token_required()
    # Check if refresh token is in DB
    user_name = authorize.get_jwt_subject()
    user = db.query(User).filter(and_(user_name == User.user_name)).first()
    if f"Bearer {user.refresh_token}" == refresh_token:
        access_token = authorize.create_access_token(subject=user_name)
        new_refresh_token = authorize.create_refresh_token(subject=user_name)

        user.refresh_token = new_refresh_token
        db.add(user)
        db.commit()
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
