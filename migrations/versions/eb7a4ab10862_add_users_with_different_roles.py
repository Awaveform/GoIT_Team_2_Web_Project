"""Add users with different roles

Revision ID: eb7a4ab10862
Revises: a2076cfbe639
Create Date: 2024-03-23 19:09:12.490221

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.services.auth import get_password_hash

# revision identifiers, used by Alembic.
revision: str = 'eb7a4ab10862'
down_revision: Union[str, None] = 'a2076cfbe639'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("INSERT INTO public.users(is_active, first_name, last_name, user_name, "
               "password, created_at) "
               f"VALUES (true, 'Admin', 'Admin', 'admin', "
               f"'{get_password_hash('admin')}', '{datetime.now()}'), "
               f"(true, 'Moderator', 'Moderator', 'moderator', "
               f"'{get_password_hash('moderator')}', '{datetime.now()}'), "
               f"(true, 'User', 'User', 'user', "
               f"'{get_password_hash('user')}', '{datetime.now()}')")

    op.execute("INSERT INTO public.users_roles(user_id, role_id, created_at) "
               f"VALUES (1, 1, '{datetime.now()}'), "
               f"(2, 2, '{datetime.now()}'), "
               f"(3, 3, '{datetime.now()}')")


def downgrade() -> None:
    pass

