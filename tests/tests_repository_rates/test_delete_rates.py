import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.repository.rates import delete_rates
from src.database.models import Rate

class TestGetRates(unittest.IsolatedAsyncioTestCase):

    def setUp(self):

        self.db = MagicMock(spec = Session)
        self.users_id = [1, 2]
        self.rates = [
            Rate(id = 1, grade = 2, photo_id = 1, created_by = self.users_id[0]),
        ]

    
    async def test_valid_arguments(self):
        self.db.delete = MagicMock()

        result = await delete_rates(
            rates = self.rates,
            db = self.db
        )
        self.assertEqual(None, result)
        self.db.delete.assert_called_once_with(self.rates[0])

    
    async def test_incorrect_argument(self):
        self.db.delete = MagicMock()

        result = await delete_rates(
            rates = [],
            db = self.db
        )

        self.db.delete.assert_not_called()