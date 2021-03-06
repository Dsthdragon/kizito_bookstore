"""Added shipping to order

Revision ID: 573eb06f3c5c
Revises: c0401ab3f0e4
Create Date: 2020-03-17 00:15:30.666414

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '573eb06f3c5c'
down_revision = 'c0401ab3f0e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('shipping', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'shipping')
    # ### end Alembic commands ###
