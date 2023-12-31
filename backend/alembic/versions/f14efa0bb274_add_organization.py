"""add organization

Revision ID: f14efa0bb274
Revises: 6a61b85da564
Create Date: 2023-06-20 16:03:58.270488

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f14efa0bb274'
down_revision = '6a61b85da564'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('checked_document', sa.Column('organization', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('checked_document', 'organization')
    # ### end Alembic commands ###
