from __future__ import annotations

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models.base import BaseFields, Base


class Rate(Base, BaseFields):
    """
    The Rate class represents the rate given by a user to a photo.

    :param id: int: The unique identifier for the rate.
    :param grade: int: The grade given by the user.
    :param photo_id: int: The ID of the photo being rated.
    :param created_by: int: The ID of the user who created the rate.
    :param created_at: datetime: The timestamp indicating when the rate was created.
    :param updated_at: datetime: The timestamp indicating when the rate was last updated.
    """
    __tablename__ = "rates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade: Mapped[int] = mapped_column(Integer)
    photo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE")
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
