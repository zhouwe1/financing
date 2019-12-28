"""'add_last_login'

Revision ID: 2cfc47570835
Revises: 1e2368a2d0b1
Create Date: 2019-12-22 14:53:24.430526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2cfc47570835'
down_revision = '1e2368a2d0b1'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_login')
    # ### end Alembic commands ###