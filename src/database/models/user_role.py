from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint

from src.database.models.base import BaseFields, Base


class UserRole(Base, BaseFields):
    """
    The UserRole class represents the role assigned to a user in the system.

    :param id: int: The unique identifier for the user role.
    :param user_id: int: The ID of the user associated with this role.
    :param role_id: int: The ID of the role associated with this user.
    :param user: User: The user associated with this user role.
    :param role: Role: The role associated with this user role.
    """
    __tablename__ = "users_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    role_id = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)

    user = relationship("User", backref="user_roles")
    role = relationship("Role")

    __table_args__ = (UniqueConstraint("user_id", "role_id"),)
