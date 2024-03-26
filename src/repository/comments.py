from datetime import timedelta, datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import PhotoComment, User
from src.schemas import CommentSchema, CommentResponse
from src.database.db import get_db

async def create_comment(body: CommentSchema, photo_id: int, created_by: User,  db: AsyncSession):
    date = datetime.now()
    comment_dct = {'comment':body.comment, "created_at": date, "photo_id": photo_id, "created_by": created_by.id}
    comment = PhotoComment(**comment_dct)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment