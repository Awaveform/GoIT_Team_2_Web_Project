from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database.models.base import Base
from src.enums import Roles


class Role(Base):
    """
    The Role class represents the role of a user in the system.

    :param id: int: The unique identifier for the role.
    :param name: str: The name of the role.
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Roles] = mapped_column(String(50), nullable=False, unique=True)
