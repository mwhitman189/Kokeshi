"""empty message

Revision ID: e848780be451
Revises: 
Create Date: 2019-01-05 03:24:57.631981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e848780be451'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customer',
    sa.Column('customerID', sa.Integer(), nullable=False),
    sa.Column('lastName', sa.String(length=64), nullable=True),
    sa.Column('firstName', sa.String(length=64), nullable=True),
    sa.Column('title', sa.String(length=32), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('customerID')
    )
    op.create_index(op.f('ix_customer_email'), 'customer', ['email'], unique=True)
    op.create_index(op.f('ix_customer_firstName'), 'customer', ['firstName'], unique=False)
    op.create_index(op.f('ix_customer_lastName'), 'customer', ['lastName'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('is_authorized', sa.Boolean(), nullable=True),
    sa.Column('password_hash', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('order',
    sa.Column('orderID', sa.Integer(), nullable=False),
    sa.Column('item', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('dob', sa.String(length=32), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('weight', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(length=300), nullable=True),
    sa.Column('isOrdered', sa.Boolean(), nullable=True),
    sa.Column('dateOrdered', sa.DateTime(), nullable=True),
    sa.Column('customer_ID', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['customer_ID'], ['customer.customerID'], ),
    sa.PrimaryKeyConstraint('orderID')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_customer_lastName'), table_name='customer')
    op.drop_index(op.f('ix_customer_firstName'), table_name='customer')
    op.drop_index(op.f('ix_customer_email'), table_name='customer')
    op.drop_table('customer')
    # ### end Alembic commands ###
