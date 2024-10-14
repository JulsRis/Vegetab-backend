"""Add ingredients relationship to User model

Revision ID: add_ingredients_to_user
Revises: 91bb051c59af
Create Date: <current_date_and_time>

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_ingredients_to_user'
down_revision = '91bb051c59af'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ingredients', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'ingredients', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ingredients', type_='foreignkey')
    op.drop_column('ingredients', 'user_id')
    # ### end Alembic commands ###
