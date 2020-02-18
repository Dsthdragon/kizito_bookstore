"""Change column name to title in Category table

Revision ID: cb4cef38cc2b
Revises: 95b2f50b1799
Create Date: 2019-11-01 09:51:17.114489

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'cb4cef38cc2b'
down_revision = '95b2f50b1799'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('title', sa.String(length=255), nullable=False))
    op.drop_column('category', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('name', mysql.VARCHAR(length=255), nullable=False))
    op.drop_column('category', 'title')
    # ### end Alembic commands ###