"""userasset_del_name_amount

Revision ID: 9d2f51a072f2
Revises: d50d9393d06a
Create Date: 2019-12-29 16:04:04.267728

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9d2f51a072f2'
down_revision = 'd50d9393d06a'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_asset', 'amount')
    op.drop_column('user_asset', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_asset', sa.Column('name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=32), nullable=True))
    op.add_column('user_asset', sa.Column('amount', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    # ### end Alembic commands ###