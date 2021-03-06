"""family_alter

Revision ID: 18002047d7cb
Revises: 7f13aad7b21b
Create Date: 2020-01-12 20:07:55.007005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18002047d7cb'
down_revision = '7f13aad7b21b'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('family', sa.Column('parent_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('family', 'parent_id')
    # ### end Alembic commands ###
