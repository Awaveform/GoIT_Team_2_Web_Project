from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean

from src.database.models.base import BaseFields, Base
from src.database.models.photo_tag import photos_tags


class Photo(Base, BaseFields):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(1000))
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    updated_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True,
    )
    original_photo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=True,
        default=None
    )
    is_transformed: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    tags = relationship("Tag", secondary="photos_tags", back_populates="photos")
