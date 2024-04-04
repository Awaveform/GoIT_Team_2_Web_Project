from __future__ import annotations

from sqlalchemy import Column, Integer, func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import Table
from sqlalchemy.sql.sqltypes import DateTime

from src.database.models.base import Base

photos_tags = Table(
    "photos_tags",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"), nullable=False),
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("updated_at", DateTime),
)
