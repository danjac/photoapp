"""Add key column to users

Revision ID: 300746e0924b
Revises: None
Create Date: 2012-09-02 23:12:07.077874

"""

# revision identifiers, used by Alembic.
revision = '300746e0924b'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('key', sa.String(30), unique=True))


def downgrade():
    op.drop_column('users', 'key')
