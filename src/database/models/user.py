from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Boolean

from src.database.models.base import BaseFields, Base


class User(Base, BaseFields):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    user_name: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(1255), nullable=True)
