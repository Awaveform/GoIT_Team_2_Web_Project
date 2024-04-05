from __future__ import annotations

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import BaseFields, Base
from src.database.models.photo_tag import photos_tags


class Tag(Base, BaseFields):
    """
    The Tag class represents a tag associated with photos in the system.

    :param id: int: The unique identifier for the tag.
    :param name: str: The name of the tag.
    :param created_by: int: The user ID of the creator of the tag.
    :param photos: Relationship: The photos associated with this tag.
    """
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    photos = relationship("Photo", secondary="photos_tags", back_populates="tags")
