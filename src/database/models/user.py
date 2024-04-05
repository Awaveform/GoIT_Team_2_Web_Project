from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Boolean

from src.database.models.base import BaseFields, Base


class User(Base, BaseFields):
    """
    The User class represents a user in the system.

    :param id: int: The unique identifier for the user.
    :param is_active: bool: Indicates if the user account is active.
    :param first_name: str: The first name of the user.
    :param last_name: str: The last name of the user.
    :param user_name: str: The username of the user.
    :param password: str: The hashed password of the user.
    :param refresh_token: str: The refresh token associated with the user's session.
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    user_name: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(1255), nullable=True)
