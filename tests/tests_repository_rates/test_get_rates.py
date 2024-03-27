import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.repository.rates import get_rates
from src.database.models import Rate

class TestGetRates(unittest.IsolatedAsyncioTestCase):

    def setUp(self):

        self.db = MagicMock(spec = Session)
        self.users_id = [1, 2]
        self.rates = [
            Rate(id = 1, grade = 2, photo_id = 1, created_by = self.users_id[0]),
        ]

    
    async def test_valid_arguments(self):
        self.db.query().filter().filter().all.return_value = self.rates

        result = await get_rates(
            db = self.db,
            photo_id = 1,
            created_by = self.users_id[0]
        )

        self.assertEqual(self.rates, result)

    
    async def test_incorrect_argument(self):
        self.db.query().all.return_value = []

        result = await get_rates(
            db = self.db,
            user = self.users_id[0]
        )

        self.assertEqual([], result)
