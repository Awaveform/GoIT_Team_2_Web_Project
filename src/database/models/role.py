from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from src.enums import Roles
from base import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Roles] = mapped_column(String(50), nullable=False, unique=True)
