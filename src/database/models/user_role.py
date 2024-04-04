from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint

from src.database.models.base import BaseFields, Base


class UserRole(Base, BaseFields):
    __tablename__ = "users_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    role_id = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "role_id"),)
