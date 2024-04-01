import unittest
from datetime import datetime

from unittest.mock import MagicMock
from sqlalchemy.orm import Session


from src.repository.comments import create_comment, get_comments

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.repository.comments import create_comment
from src.database.models import PhotoComment, User, Photo
from src.schemas import CommentSchema


class TestCommentPhoto(unittest.IsolatedAsyncioTestCase):
class TestCreateCommentPhoto(unittest.IsolatedAsyncioTestCase):

    def setUp(self):

        self.db = MagicMock(spec=Session)
        self.user = User(id=1)
        self.existing_photo = Photo(id=1)
        self.comment = CommentSchema(comment='Test comment')
        self.created_at=datetime.now()

        
    async def test_create_comment_success(self):

        result: PhotoComment = await create_comment(
            photo_id=self.existing_photo,
            comment=self.comment,
            current_user=self.user,
            db=self.db
        )
        self.assertEqual(result.comment, 'Test comment')
        
        self.assertEqual(result.created_by, self.user.id)
        self.db.add.assert_called_once_with(result)


    async def test_get_comments_valid_list(self):
        expected_comments: list[PhotoComment] = [
                        PhotoComment(
                id=1,
                comment="Test comment 1",
                created_at=self.created_at,
                updated_at=None,
                photo_id=self.existing_photo,
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
        self.db.execute.return_value.scalars.return_value.all.return_value = (
            expected_comments
        )

        comments = await get_comments(photo_id=1, limit=10, offset=0, db=self.db)
        self.assertEqual(comments, expected_comments)
        self.assertEqual(comments[0].comment, "Test comment 1")
        self.assertEqual(comments[1].comment, "Test comment 2")

    async def test_get_comments_invalid_photo_id(self):
        self.db.execute.return_value.scalars.return_value.all.return_value = []

        comments = await get_comments(photo_id=999, limit=10, offset=0, db=self.db)
        self.assertEqual(comments, [])

    async def test_get_comments_invalid_offset(self):
        self.db.execute.return_value.scalars.return_value.all.return_value = []

        comments = await get_comments(photo_id=1, limit=10, offset=-10, db=self.db)
        self.assertEqual(comments, [])
