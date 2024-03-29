import unittest
from datetime import datetime
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

from src.database.models import PhotoComment, User
from src.schemas import CommentSchema
from src.repository.comments import get_comments


class TestGetComments(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1)
        self.session = MagicMock(spec=Session)

    async def test_get_comments_valid_list(self):
        comments_data = [
            PhotoComment(
                id=1,
                comment="Test comment 1",
                created_at=datetime.now(),
                updated_at=None,
                photo_id=1,
                created_by=self.user.id,
            ),
            PhotoComment(
                id=2,
                comment="Test comment 2",
                created_at=datetime.now(),
                updated_at=None,
                photo_id=1,
                created_by=self.user.id,
            ),
        ]
        self.session.execute.return_value.scalars.return_value.all.return_value = (
            comments_data
        )

        comments = await get_comments(photo_id=1, limit=10, offset=0, db=self.session)
        self.assertEqual(comments, comments_data)
        self.assertEqual(comments[0].comment, "Test comment 1")
        self.assertEqual(comments[1].comment, "Test comment 2")

    async def test_get_comments_invalid_photo_id(self):
        self.session.execute.return_value.scalars.return_value.all.return_value = []

        comments = await get_comments(photo_id=999, limit=10, offset=0, db=self.session)
        self.assertEqual(comments, [])

    async def test_get_comments_invalid_offset(self):
        self.session.execute.return_value.scalars.return_value.all.return_value = []

        comments = await get_comments(photo_id=1, limit=10, offset=-1, db=self.session)
        self.assertEqual(comments, [])
