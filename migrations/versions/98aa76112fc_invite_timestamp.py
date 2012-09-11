"""Invite timestamp

Revision ID: 98aa76112fc
Revises: None
Create Date: 2012-09-11 17:25:44.064635

"""

# revision identifiers, used by Alembic.
revision = '98aa76112fc'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.alter_column('invites', 'created_on', name='created_at')
    ### end Alembic commands ###


def downgrade():
    op.alter_column('invites', 'created_at', name='created_on')
    ### end Alembic commands ###
