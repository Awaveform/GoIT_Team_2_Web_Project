import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.repository.comments import create_comment
from src.database.models import PhotoComment, User, Photo
from src.schemas import CommentSchema


class TestCreateCommentPhoto(unittest.IsolatedAsyncioTestCase):

    def setUp(self):

        self.db = MagicMock(spec=Session)
        self.user = User(id=1)
        self.existing_photo = Photo(id=1)
        self.comment = CommentSchema(comment='Test comment')
        
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
