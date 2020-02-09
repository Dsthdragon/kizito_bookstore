"""Changed column role to title in role table

Revision ID: 95b2f50b1799
Revises: f18377a6e8b9
Create Date: 2019-10-31 00:48:18.832954

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '95b2f50b1799'
down_revision = 'f18377a6e8b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role', sa.Column('title', sa.String(length=100), nullable=False))
    op.drop_column('role', 'role')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role', sa.Column('role', mysql.VARCHAR(length=100), nullable=False))
    op.drop_column('role', 'title')
    # ### end Alembic commands ###
