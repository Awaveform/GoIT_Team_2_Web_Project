"""Add unique constraint for users_roles table

Revision ID: c414ceaf5032
Revises: 25d49e10d580
Create Date: 2024-04-04 13:24:07.063085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c414ceaf5032"
down_revision: Union[str, None] = "25d49e10d580"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_user_id_role_id", "users_roles", ["user_id", "role_id"], schema="public"
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_id_role_id", "users_roles", schema="public")
