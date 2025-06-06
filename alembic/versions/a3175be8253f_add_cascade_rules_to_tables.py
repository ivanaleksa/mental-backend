"""Add cascade rules to tables

Revision ID: a3175be8253f
Revises: 9864a7d414bc
Create Date: 2025-05-20 16:15:10.247114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3175be8253f'
down_revision: Union[str, None] = '9864a7d414bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('client_psychologist_client_id_fkey', 'client_psychologist', type_='foreignkey')
    op.drop_constraint('client_psychologist_psychologist_id_fkey', 'client_psychologist', type_='foreignkey')
    op.create_foreign_key(None, 'client_psychologist', 'psychologists', ['psychologist_id'], ['psychologist_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'client_psychologist', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.drop_constraint('client_requests_client_id_fkey', 'client_requests', type_='foreignkey')
    op.create_foreign_key(None, 'client_requests', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.drop_constraint('confirmation_requests_psychologist_id_fkey', 'confirmation_requests', type_='foreignkey')
    op.drop_constraint('confirmation_requests_client_id_fkey', 'confirmation_requests', type_='foreignkey')
    op.create_foreign_key(None, 'confirmation_requests', 'psychologists', ['psychologist_id'], ['psychologist_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'confirmation_requests', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.drop_constraint('notes_client_id_fkey', 'notes', type_='foreignkey')
    op.create_foreign_key(None, 'notes', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.drop_constraint('psychologist_requests_client_id_fkey', 'psychologist_requests', type_='foreignkey')
    op.drop_constraint('psychologist_requests_psychologist_id_fkey', 'psychologist_requests', type_='foreignkey')
    op.create_foreign_key(None, 'psychologist_requests', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'psychologist_requests', 'psychologists', ['psychologist_id'], ['psychologist_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'psychologist_requests', type_='foreignkey')
    op.drop_constraint(None, 'psychologist_requests', type_='foreignkey')
    op.create_foreign_key('psychologist_requests_psychologist_id_fkey', 'psychologist_requests', 'psychologists', ['psychologist_id'], ['psychologist_id'])
    op.create_foreign_key('psychologist_requests_client_id_fkey', 'psychologist_requests', 'clients', ['client_id'], ['client_id'])
    op.drop_constraint(None, 'notes', type_='foreignkey')
    op.create_foreign_key('notes_client_id_fkey', 'notes', 'clients', ['client_id'], ['client_id'])
    op.drop_constraint(None, 'confirmation_requests', type_='foreignkey')
    op.drop_constraint(None, 'confirmation_requests', type_='foreignkey')
    op.create_foreign_key('confirmation_requests_client_id_fkey', 'confirmation_requests', 'clients', ['client_id'], ['client_id'])
    op.create_foreign_key('confirmation_requests_psychologist_id_fkey', 'confirmation_requests', 'psychologists', ['psychologist_id'], ['psychologist_id'])
    op.drop_constraint(None, 'client_requests', type_='foreignkey')
    op.create_foreign_key('client_requests_client_id_fkey', 'client_requests', 'clients', ['client_id'], ['client_id'])
    op.drop_constraint(None, 'client_psychologist', type_='foreignkey')
    op.drop_constraint(None, 'client_psychologist', type_='foreignkey')
    op.create_foreign_key('client_psychologist_psychologist_id_fkey', 'client_psychologist', 'psychologists', ['psychologist_id'], ['psychologist_id'])
    op.create_foreign_key('client_psychologist_client_id_fkey', 'client_psychologist', 'clients', ['client_id'], ['client_id'])
    # ### end Alembic commands ###
