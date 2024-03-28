import unittest
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta, date


from sqlalchemy.ext.asyncio import AsyncSession
import asyncio


from src.database.models import PhotoComment, User
from src.schemas import CommentSchema, CommentResponse
from src.repository.comments import create_comment


class TestAsyncComments(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, user_name='admin', password='admin')
        self.session=AsyncMock(spec=AsyncSession)


    async def test_create_comment_success(self):
        body = CommentSchema(comment='test_comment', 
                             created_at=datetime.now(), 
                             updated_at=None, 
                             photo_id=1, 
                             created_by=self.user.id)
        result = await create_comment(body, 1, self.user, self.session)
        self.assertIsInstance(result, PhotoComment)
        self.assertEqual(result.comment, body.comment)
        self.assertEqual(result.photo_id, 1)
        self.assertEqual(result.created_by, self.user)
        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)


    
    async def test_create_comment_failure_missing_body(self):
        # Arrange
        body = None
        photo_id = 1
        created_by = 1
        db = AsyncMock()
        
        # Act & Assert
        with self.assertRaises(AttributeError) as context:
            await create_comment(body, photo_id, created_by, db)
        
        self.assertEqual(str(context.exception), "'NoneType' object has no attribute 'comment'")
        



