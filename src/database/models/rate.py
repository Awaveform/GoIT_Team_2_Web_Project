from __future__ import annotations

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models.base import BaseFields, Base


class Rate(Base, BaseFields):
    __tablename__ = "rates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade: Mapped[int] = mapped_column(Integer)
    photo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE")
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
