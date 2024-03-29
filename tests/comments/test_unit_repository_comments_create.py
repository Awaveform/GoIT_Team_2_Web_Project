import unittest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from src.database.models import PhotoComment, User
from src.schemas import CommentSchema
from src.repository.comments import get_photo_by_id, get_user_by_id, create_comment


class TestCommentService(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1)
        self.session = MagicMock(spec=Session)

    @patch("src.repository.comments.get_photo_by_id", return_value=MagicMock())
    @patch("src.repository.comments.get_user_by_id", return_value=MagicMock())
    async def test_create_comment_positive_flow(self, mock_get_user_by_id, mock_get_photo_by_id):
        body = CommentSchema(
            comment="test_comment",
            created_at=datetime.now(),
            updated_at=None,
            photo_id=1,
            created_by=self.user.id,
        )
        result = await create_comment(body, 1, self.user.id, self.session)
        self.assertIsInstance(result, PhotoComment)
        self.assertEqual(result.comment, body.comment)
        self.assertEqual(result.photo_id, 1)
        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)

    @patch("src.repository.comments.get_photo_by_id", return_value=None)
    async def test_create_comment_photo_not_found(self, mock_get_photo_by_id):
        async with AsyncSession() as db:
            body = CommentSchema(
                comment="test_comment",
                created_at=datetime.now(),
                updated_at=None,
                photo_id=1,
                created_by=self.user.id,
            )
            with self.assertRaises(HTTPException) as context:
                await create_comment(body, body.photo_id, body.created_by, db)
            self.assertEqual(context.exception.status_code, 400)

    @patch("src.repository.comments.get_photo_by_id", return_value=AsyncMock())
    @patch("src.repository.comments.get_user_by_id", return_value=None)
    async def test_create_comment_user_not_found(
        self, mock_get_user_by_id, mock_get_photo_by_id
    ):
        async with AsyncSession() as db:
            body = CommentSchema(
                comment="test_comment",
                created_at=datetime.now(),
                updated_at=None,
                photo_id=1,
                created_by=self.user.id,
            )
            with self.assertRaises(HTTPException) as context:
                await create_comment(body, body.photo_id, body.created_by, db)
            self.assertEqual(context.exception.status_code, 400)
