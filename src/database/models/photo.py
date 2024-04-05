from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean

from src.database.models.base import BaseFields, Base
from src.database.models.photo_tag import photos_tags
from src.database.models.tag import Tag


class Photo(Base, BaseFields):
    """
    Photo database model.

    :param id: Mapped[int]: The unique identifier for the photo.
    :type id: Mapped[int]
    :param url: Mapped[str]: The URL of the photo.
    :type url: Mapped[str]
    :param description: Mapped[str]: The description of the photo. Defaults to None.
    :type description: Mapped[str]
    :param created_by: Mapped[int]: The user ID of the creator of the photo.
    :type created_by: Mapped[int]
    :param updated_by: Mapped[int]: The user ID of the last updater of the photo. Defaults to None.
    :type updated_by: Mapped[int]
    :param original_photo_id: Mapped[int]: The ID of the original photo if it is a transformed version. Defaults to None.
    :type original_photo_id: Mapped[int]
    :param is_transformed: Mapped[bool]: Indicates if the photo is a transformed version. Defaults to False.
    :type is_transformed: Mapped[bool]
    :param tags: Relationship: The tags associated with the photo.
    :type tags: Relationship
    """
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(1000))
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    updated_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    original_photo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("photos.id", ondelete="CASCADE"),
        nullable=True,
        default=None,
    )
    is_transformed: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    tags = relationship("Tag", secondary="photos_tags", back_populates="photos")
