import unittest
from typing import Type
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.database.models import User, Photo
from src.repository.photos import (
    get_photos_by_user_id,
    get_photo_by_photo_id,
    create_photo,
    delete_photo_by_id)


class TestPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.photo_url = "https://res.cloudinary.com/image/upload/6AQ8KKI6.jpg"
        self.photo_id = 1

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

    async def test_get_photo_by_photo_id(self):
        expected_photo: Photo = Photo(created_by=self.user.id)
        self.session.query().filter().first.return_value = expected_photo
        actual_photo: Type[Photo] = await get_photo_by_photo_id(
            photo_id=self.user.id, db=self.session
        )
        assert actual_photo == expected_photo

    async def test_create_photo(self):
        current_user = User(user_name='test_user', id=1)
        file = MagicMock()

        with patch('src.repository.photos._upload_photo_to_cloudinary',
                   return_value='https://example.com/photo.jpg') as mock_upload_photo_to_cloudinary:

            photo = await create_photo(description='Test photo', current_user=current_user, db=self.session, file=file)

            assert photo.url == 'https://example.com/photo.jpg'

            mock_upload_photo_to_cloudinary.assert_called_once_with(current_user=current_user, file=file)

    async def test_create_photo_negative(self):
        current_user = User(user_name='test_user', id=1)
        file = MagicMock()

        with patch('src.repository.photos._upload_photo_to_cloudinary') as mock_upload_photo_to_cloudinary:
            mock_upload_photo_to_cloudinary.side_effect = HTTPException(status_code=500, detail="Upload failed")

            with self.assertRaises(HTTPException):
                await create_photo(description='Test photo', current_user=current_user, db=self.session, file=file)

    async def test_delete_photo_by_id(self):
        current_user = User(user_name='test_user', id=1)
        photo = Photo(id=self.photo_id, url=self.photo_url,
                      created_by=current_user.id)
        self.session.query().filter().first.return_value = photo

        with patch('src.repository.photos._delete_photo_from_cloudinary') as mock_delete_photo_from_cloudinary:
            deleted_photo = await delete_photo_by_id(photo=photo, db=self.session)

            self.assertEqual(deleted_photo, photo)
            mock_delete_photo_from_cloudinary.assert_called_once_with(photo_url=photo.url)
