"""fp_type

Revision ID: a45acd478334
Revises: 5ba4d521bbf7
Create Date: 2019-12-28 22:36:08.626696

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a45acd478334'
down_revision = '5ba4d521bbf7'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('financial_product', sa.Column('type', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'financial_product', 'fp_type', ['type'], ['id'], ondelete='RESTRICT')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'financial_product', type_='foreignkey')
    op.drop_column('financial_product', 'type')
    # ### end Alembic commands ###