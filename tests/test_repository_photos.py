import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.database.models.photo import Photo
from src.database.models.user import User
from src.repository.photos import get_photo_by_photo_id, create_photo


class TestPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.photo_url = "https://res.cloudinary.com/image/upload/6AQ8KKI6.jpg"
        self.photo_id = 1

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
        actual_photo: Photo = await get_photo_by_photo_id(photo_id=1, db=self.session)
        assert actual_photo is None

    async def test_create_photo(self):
        current_user = User(user_name="test_user", id=1)
        file = MagicMock()

        with patch(
            "src.repository.photos._upload_photo_to_cloudinary",
            return_value="https://example.com/photo.jpg",
        ) as mock_upload_photo_to_cloudinary:
            photo = await create_photo(
                description="Test photo",
                current_user=current_user,
                db=self.session,
                file=file,
            )

            assert photo.url == "https://example.com/photo.jpg"

            mock_upload_photo_to_cloudinary.assert_called_once_with(
                current_user=current_user, file=file
            )

    async def test_create_photo_negative(self):
        current_user = User(user_name="test_user", id=1)
        file = MagicMock()

        with patch(
            "src.repository.photos._upload_photo_to_cloudinary"
        ) as mock_upload_photo_to_cloudinary:
            mock_upload_photo_to_cloudinary.side_effect = HTTPException(
                status_code=500, detail="Upload failed"
            )

            with self.assertRaises(HTTPException):
                await create_photo(
                    description="Test photo",
                    current_user=current_user,
                    db=self.session,
                    file=file,
                )
