"""Added Store Address to order model

Revision ID: dbdc74926faf
Revises: 573eb06f3c5c
Create Date: 2020-04-18 15:32:25.481011

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'dbdc74926faf'
down_revision = '573eb06f3c5c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('store_address_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order', 'store_address', ['store_address_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'store_address_id')
    # ### end Alembic commands ###
