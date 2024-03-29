import unittest

from unittest.mock import MagicMock
from sqlalchemy.orm import Query

from src.repository.rates import _filter_by
from src.database.models import Rate


class TestFilterBy(unittest.IsolatedAsyncioTestCase):

    def setUp(self):

        self.query = MagicMock(spec=Query[Rate])
        self.filter_by_data = {
            "photo_id": 1,
            "created_by": 2
        }
    
    async def test_valid_arguments(self):
        self.query.filter().filter.return_value = self.query

        result = await _filter_by(query=self.query, **self.filter_by_data)

        self.assertEqual(self.query, result)

    async def test_incorrect_argument(self):
        self.filter_by_data.update({"user_id": 2, "id": 1})
        self.query.filter().filter().filter.return_value = self.query

        result = await _filter_by(query=self.query, **self.filter_by_data)

        self.assertEqual(self.query, result)

    async def test_without_sort_arguments(self):
        result = await _filter_by(query=self.query)
        
        self.assertEqual(self.query, result)
