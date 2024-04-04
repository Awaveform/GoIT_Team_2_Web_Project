"""Add roles to DB

Revision ID: a2076cfbe639
Revises: d4d24cad6ccb
Create Date: 2024-03-23 10:39:43.870691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a2076cfbe639"
down_revision: Union[str, None] = "d4d24cad6ccb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO public.roles(name) VALUES ('admin'), ('moderator'), ('user')"
    )


def downgrade() -> None:
    pass
