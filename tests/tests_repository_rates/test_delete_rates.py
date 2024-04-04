import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.repository.rates import delete_rates
from src.database.models.rate import Rate


class TestGetRates(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.users_id = {"admin": 1, "user": 2}
        self.rates_id = [1, 2, 3]
        self.rates = [
            Rate(id=1, grade=2, photo_id=1, created_by=self.users_id["admin"]),
        ]

    async def test_valid_arguments(self):
        self.db.query().filter().delete = MagicMock()

        result = await delete_rates(rates_id=self.rates_id, db=self.db)
        self.assertEqual(None, result)

    async def test_incorrect_argument(self):
        self.db.query().filter().delete = MagicMock()

        result = await delete_rates(rates_id=[], db=self.db)

        self.assertEqual(None, result)
