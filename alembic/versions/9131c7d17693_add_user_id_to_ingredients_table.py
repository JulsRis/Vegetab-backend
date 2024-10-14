"""Add user_id to ingredients table

Revision ID: 9131c7d17693
Revises: add_ingredients_to_user
Create Date: 2024-10-08 02:53:44.577277

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9131c7d17693'
down_revision: Union[str, None] = 'add_ingredients_to_user'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_user_id_users', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_id_users', type_='foreignkey')
        batch_op.drop_column('user_id')
