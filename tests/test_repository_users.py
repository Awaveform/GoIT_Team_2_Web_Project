from __future__ import annotations

import random
from datetime import datetime
from typing import Type, Tuple
from unittest.mock import MagicMock, AsyncMock
import unittest

from sqlalchemy.orm import Session

from src.database.models import User, Role, UserRole
from src.schemas import UserModel, UserRoleModel
from src.enums import Roles
from src.repository.users import (
    get_role,
    get_user_role,
    assign_role_to_user,
    get_user_by_user_name,
    create_user,
    get_full_user_info_by_name,
    assign_user_role,
    update_token,
)


async def async_none() -> None:
    """
    Method to return coroutine as a None value.
    :return: Coroutine with None value.
    :rtype: None.
    """
    return None


class TestRolesAndUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.redis = AsyncMock()
        self.user = User(id=1)

    async def test_get_roles(self):
        for role, role_id in zip(list(Roles), [1, 2, 3]):
            expected_role = Role(name=role.value, id=role_id)
            self.session.query().filter().first.return_value = expected_role
            self.redis.get.return_value = await async_none()
            actual_role = await get_role(_role=role, db=self.session, r=self.redis)
            assert actual_role.name == expected_role.name

    async def test_get_user_roles(self):
        for role, user_id in zip(list(Roles), [1, 2, 3]):
            expected_role = Role(name=role.value)
            self.session.query().join().filter().first.return_value = expected_role
            self.redis.get.return_value = await async_none()
            actual_role: Type[Role] = await get_user_role(
                user_id=user_id, db=self.session, r=self.redis
            )
            assert actual_role.name == expected_role.name

    async def test_assign_role_to_user(self):
        roles = [Role(name=role.value) for role in list(Roles)]
        for role, user_id in zip(roles, [1, 2, 3]):
            new_user_role: UserRole = await assign_role_to_user(
                user_id=self.user.id, role=role, db=self.session
            )
            assert new_user_role.role_id == role.id

    async def test_get_user_by_user_name(self):
        user_names = ["admin1", "moderator1", "user1"]
        for user_name in user_names:
            expected_user: User = User(user_name=user_name)
            self.session.query().filter().first.return_value = expected_user
            self.redis.get.return_value = await async_none()
            user: Type[User] = await get_user_by_user_name(
                user_name=user_name, db=self.session, r=self.redis
            )
            assert user.user_name == user_name

    async def test_create_user(self):
        for role_name, role_id in zip(list(Roles), [1, 2, 3]):
            user: UserModel = UserModel(
                first_name=f"Test_{role_name.value}",
                last_name=f"Test_{role_name.value}",
                user_name=f"test_{role_name.value}",
                password="password",
            )

            expected_role = Role(id=role_id, name=role_name.value)
            self.session.query().filter().first.return_value = expected_role
            self.redis.get.return_value = await async_none()

            actual_user, actual_role = await create_user(
                body=user, role=role_name, db=self.session, r=self.redis
            )
            assert actual_user.user_name == user.user_name
            assert actual_user.first_name == user.first_name
            assert actual_user.last_name == user.last_name
            assert actual_user.password == user.password
            assert actual_role.role_id == role_id

    async def test_get_full_user_info_by_name(self):
        user_names = ["admin2", "moderator2", "user2"]
        for user_name in user_names:
            expected_user: User = User(user_name=user_name)
            self.session.query().filter().first.return_value = expected_user
            self.redis.get.return_value = await async_none()
            actual_user: Tuple[User, int] = await get_full_user_info_by_name(
                user_name=user_name, db=self.session, r=self.redis
            )
            assert actual_user[0].user_name == user_name
            assert actual_user[1] == 0

    async def test_assign_user_role(self):
        roles = user_ids = [1, 2, 3]
        for role_id, user_id in zip(roles, user_ids):
            body = UserRoleModel(
                user_id=user_id,
                role_id=role_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            user_role: UserRole = await assign_user_role(body=body, db=self.session)
            assert user_role.role_id == role_id
            assert user_role.user_id == user_id

    async def test_update_token(self):
        await update_token(
            user=self.user, token=str(random.randint(1, 10)), db=self.session
        )
