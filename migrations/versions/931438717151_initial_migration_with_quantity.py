"""Initial migration with quantity

Revision ID: 931438717151
Revises: 
Create Date: 2024-11-28 19:33:11.730573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '931438717151'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('course_group', sa.String(length=10), nullable=False),
    sa.Column('destination', sa.String(length=200), nullable=False),
    sa.Column('request_type', sa.String(length=50), nullable=False),
    sa.Column('period_start', sa.Date(), nullable=True),
    sa.Column('period_end', sa.Date(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('archived', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('request')
    # ### end Alembic commands ###