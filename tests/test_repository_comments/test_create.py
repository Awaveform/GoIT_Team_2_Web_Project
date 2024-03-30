import unittest

from unittest.mock import MagicMock
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.repository.comments import create_comment
from src.database.models import PhotoComment, User
from src.schemas import CommentSchema


class TestCreateRatePhoto(unittest.IsolatedAsyncioTestCase):

    def setUp(self):

        self.db = MagicMock(spec=Session)
        self.user = User(id=1)
        

    async def test_create_comment_success(self):

        result: PhotoComment = await create_comment(
            photo_id=1,
            comment=CommentSchema(comment='Test comment'),
            current_user=self.user,
            db=self.db
        )
        self.assertEqual(result.comment, 'Test comment')
        self.assertEqual(result.created_by, self.user.id)
        self.db.add.assert_called_once_with(result)

        

