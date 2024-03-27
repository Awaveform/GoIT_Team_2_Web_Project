import pytest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from datetime import datetime

from src.repository.users import get_current_user
from src.services.auth import get_password_hash
from src.database.models import User, Photo, Role
from main import app


@pytest.fixture(scope="module")
def add_data_to_table(session):
    user = User(
        first_name = "Admin",
        last_name = "Admin",
        user_name = "admin",
        password = "admin"
    )
    role = Role()



@pytest.fixture()
def auht_user():
    user = User(
        id = 1,
        is_active = True,
        first_name = "Admin",
        last_name = "Admin",
        user_name = "admin",
        password = get_password_hash("admin"),
        created_at = datetime(2024, 3, 27),
        updated_at = None,
        refresh_token = None
    )
    
    def override_get_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    return user
    

def test_grade_out_of_range_error(client, auht_user):
    
    response = client.post(
        "/api/rates/1",
        json={"grade": 6}
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "The grade must be greater than 0 and less than or equal to 5."


def test_evaluate_photo_by_owner(client, auht_user, session):
    photo = Photo(
        url = "http://",
        description = "description",
        created_by = auht_user.id
    )
    
    # session.add(User(is_active = True,
    #     first_name = "Admin",
    #     last_name = "Admin",
    #     user_name = "admin",
    #     password = get_password_hash("admin"),))
    # session.add(photo)
    # session.commit()

    response = client.post(
        "/api/rates/1",
        json={"grade": 4}
    )
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == "Owner of a photo has not availability to rate the photo."


def test_rate_photo_once():
    pass

def test_create_rate_photo():
    pass
