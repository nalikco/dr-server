"""empty message

Revision ID: 407197847838
Revises: bed0c9cb52cd
Create Date: 2020-11-19 21:43:10.341332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '407197847838'
down_revision = 'bed0c9cb52cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('expense',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('liquid_id', sa.Integer(), nullable=True),
    sa.Column('vehicle_id', sa.Integer(), nullable=True),
    sa.Column('worker_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2, asdecimal=False), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('purpose', sa.String(length=200), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['liquid_id'], ['liquids.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['worker_id'], ['workers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('expense')
    # ### end Alembic commands ###