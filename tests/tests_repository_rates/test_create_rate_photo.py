import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.repository.rates import create_rate_photo
from src.database.models.rate import Rate


class TestCreateRatePhoto(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.users_id = {"admin": 1, "user": 2}

    async def test_valid_arguments(self):
        result: Rate = await create_rate_photo(
            photo_id=1, grade=3, user_id=self.users_id["admin"], db=self.db
        )
        self.assertEqual(3, result.grade)
        self.assertEqual(1, result.photo_id)
        self.assertEqual(self.users_id["admin"], result.created_by)
        self.db.add.assert_called_once_with(result)
