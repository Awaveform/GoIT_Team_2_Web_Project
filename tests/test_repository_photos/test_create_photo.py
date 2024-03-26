from http.client import HTTPException

import pytest
from unittest.mock import patch, MagicMock  # For mocking external dependencies

from src.database.models import User  # Assuming User model is in your_app.models
from src.repository.photos import upload_photo_to_cloudinary
from src.conf.config import settings  # Assuming settings access


@pytest.fixture
def mock_cloudinary_uploader():
    """Fixture to mock cloudinary.uploader"""
    return MagicMock()


@pytest.mark.parametrize('description', [None, 'Test photo'])
def test_upload_success(mock_cloudinary_uploader, description):
    """
    Tests successful upload with and without description.
    """
    # Create mock user and file objects
    mock_user = User(user_name='test_user')
    mock_file = MagicMock(filename='test_image.jpg')

    # Set up expected upload result and URL
    expected_upload_result = {'secure_url': 'https://cloudinary.com/test_image.jpg'}
    mock_cloudinary_uploader.upload.return_value = expected_upload_result

    # Patch cloudinary.uploader with the fixture
    with patch('src.repository.photos.cloudinary.uploader', mock_cloudinary_uploader):
        # Call the function
        photo_url = upload_photo_to_cloudinary(mock_user, mock_file, description=description)

    # Assertions
    assert photo_url == expected_upload_result['secure_url']

    # Verify cloudinary config and upload calls
    mock_cloudinary_uploader.config.assert_called_once_with(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    expected_public_id = f'PhotoShareApp/test_user/{str(mock_file.filename).split(".")[0] + "." + str(mock_file.filename).split(".")[-1].lower()}'
    mock_cloudinary_uploader.upload.assert_called_once_with(mock_file.file, public_id=expected_public_id)


def test_upload_failure_unsupported_format():
    """
    Tests upload failure for unsupported file format.
    """
    # Create mock user and file objects
    mock_user = User(user_name='test_user')
    mock_file = MagicMock(filename='test_image.gif')

    # Expected exception
    with pytest.raises(HTTPException) as excinfo:
        upload_photo_to_cloudinary(mock_user, mock_file)

    assert excinfo.type == HTTPException
    assert excinfo.value.status_code == 400
    assert "Unsupported file format" in str(excinfo.value.detail)
