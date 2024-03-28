"""Add columns to Photo db model

Revision ID: 7551c214bf17
Revises: eb7a4ab10862
Create Date: 2024-03-28 13:02:37.014521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7551c214bf17'
down_revision: Union[str, None] = 'eb7a4ab10862'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photos', sa.Column('original_photo_id', sa.Integer(), nullable=True))
    op.add_column('photos', sa.Column('is_transformed', sa.Boolean(), nullable=True))
    op.create_foreign_key(None, 'photos', 'photos', ['original_photo_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'photos', type_='foreignkey')
    op.drop_column('photos', 'is_transformed')
    op.drop_column('photos', 'original_photo_id')
    # ### end Alembic commands ###
