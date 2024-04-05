from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey

from src.database.models.base import BaseFields, Base


class PhotoComment(Base, BaseFields):
    """
    Photo comment database model.

    :param id: Mapped[int]: The unique identifier for the comment.
    :type id: Mapped[int]
    :param comment: Mapped[str]: The content of the comment.
    :type comment: Mapped[str]
    :param photo_id: Mapped[int]: The ID of the photo to which the comment belongs.
    :type photo_id: Mapped[int]
    :param created_by: Mapped[int]: The user ID of the creator of the comment.
    :type created_by: Mapped[int]
    """
    __tablename__ = "photos_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(String(500), nullable=False)
    photo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE")
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
