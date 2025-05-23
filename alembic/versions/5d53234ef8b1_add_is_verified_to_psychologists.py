"""add is_verified to psychologists

Revision ID: 5d53234ef8b1
Revises: a3175be8253f
Create Date: 2025-05-22 13:41:56.542026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d53234ef8b1'
down_revision: Union[str, None] = 'a3175be8253f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('psychologists', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('true')))
    op.alter_column('clients', 'is_verified', server_default=None)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('psychologists', 'is_verified')
    # ### end Alembic commands ###
