"""add datetime field to vet document

Revision ID: 6a61b85da564
Revises: dffb20929065
Create Date: 2023-06-07 23:25:25.054885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a61b85da564'
down_revision = 'dffb20929065'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('checked_document', sa.Column('saved_datetime', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('checked_document', 'saved_datetime')
    # ### end Alembic commands ###