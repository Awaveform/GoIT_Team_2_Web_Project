import unittest
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta, date

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import PhotoComment, User
from src.schemas import CommentSchema, CommentResponse
from src.repository.comments import create_comment


class TestAsyncComments(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, user_name='admin', password='admin')
        self.session=AsyncMock(spec=AsyncSession)


    async def test_create_comment(self):
        body = CommentSchema(comment='test_comment')
        result = await create_comment(body, 1, self.user, self.session)
        self.assertIsInstance(result, PhotoComment)
        self.assertEqual(result.comment, body.comment)


