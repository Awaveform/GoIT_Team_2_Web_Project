import unittest
from typing import Type
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User, Photo
from src.repository.photos import get_photos_by_user_id, get_photo_by_photo_id


class TestPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_photos_by_user_id(self):
        expected_photos: list[Photo] = [
            Photo(created_by=self.user.id),
            Photo(created_by=self.user.id),
            Photo(created_by=self.user.id),
        ]
        self.session.query().filter().all.return_value = expected_photos
        actual_photos: list[Type[Photo]] = await get_photos_by_user_id(
            user_id=self.user.id, db=self.session
        )
        assert actual_photos == expected_photos

    async def test_get_photos_by_user_id_negative(self):
        expected_photos: list[Photo] = []
        self.session.query().filter().all.return_value = expected_photos
        actual_photos: list[Type[Photo]] = await get_photos_by_user_id(
            user_id=self.user.id, db=self.session
        )
        assert actual_photos == expected_photos

    async def test_get_photo_by_photo_id(self):
        expected_photo: Photo = Photo(created_by=self.user.id)
        self.session.query().filter().first.return_value = expected_photo
        actual_photo: Photo = await get_photo_by_photo_id(
            photo_id=self.user.id, db=self.session
        )
        assert actual_photo == expected_photo

    async def test_get_photo_by_photo_id_negative(self):
        expected_photo: Photo = None
        self.session.query().filter().first.return_value = expected_photo
        actual_photo: Photo = await get_photo_by_photo_id(
            photo_id=1, db=self.session
        )
        assert actual_photo is None
