"""created category_filters and product_filters table

Revision ID: 399549c08a2a
Revises: cd94e2a90b09
Create Date: 2019-11-13 22:05:12.208403

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '399549c08a2a'
down_revision = 'cd94e2a90b09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category_filters',
    sa.Column('filter_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['filter_id'], ['filter.id'], ),
    sa.PrimaryKeyConstraint('filter_id', 'category_id')
    )
    op.drop_table('category_filter')
    op.drop_table('product_filter')
    op.drop_constraint('product_filters_ibfk_1', 'product_filters', type_='foreignkey')
    op.drop_column('product_filters', 'filter_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product_filters', sa.Column('filter_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.create_foreign_key('product_filters_ibfk_1', 'product_filters', 'filter', ['filter_id'], ['id'])
    op.create_table('product_filter',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('product_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('value_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('filter_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['filter_id'], ['filter.id'], name='product_filter_ibfk_1'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], name='product_filter_ibfk_2'),
    sa.ForeignKeyConstraint(['value_id'], ['filter_value.id'], name='product_filter_ibfk_3'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('category_filter',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('category_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('filter_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('created', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], name='category_filter_ibfk_1'),
    sa.ForeignKeyConstraint(['filter_id'], ['filter.id'], name='category_filter_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.drop_table('category_filters')
    # ### end Alembic commands ###