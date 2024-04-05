from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseFields:
    """
    Base fields for database models.

    :param created_at: Mapped[datetime]: The timestamp when the record was created.
    :type created_at: Mapped[datetime]
    :param updated_at: Mapped[datetime]: The timestamp when the record was last updated.
                        Defaults to None, but automatically updates to the current timestamp on update.
    :type updated_at: Mapped[datetime]
    """
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, onupdate=func.now()
    )
