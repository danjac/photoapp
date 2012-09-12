"""cascade deletes

Revision ID: 39440ceaa03c
Revises: 98aa76112fc
Create Date: 2012-09-11 20:38:29.375496

"""

# revision identifiers, used by Alembic.
revision = '39440ceaa03c'
down_revision = '98aa76112fc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.execute("""
    ALTER TABLE invites
        DROP CONSTRAINT invites_sender_id_fkey,
        ADD CONSTRAINT invites_sender_id_fkey
            FOREIGN KEY (sender_id)
            REFERENCES users (id)
                ON UPDATE NO ACTION
                ON DELETE CASCADE;

    ALTER TABLE tags
        DROP CONSTRAINT tags_owner_id_fkey,
        ADD CONSTRAINT tags_owner_id_fkey
            FOREIGN KEY (owner_id)
            REFERENCES users (id)
                ON UPDATE NO ACTION
                ON DELETE CASCADE;

    ALTER TABLE photos
        DROP CONSTRAINT photos_owner_id_fkey,
        ADD CONSTRAINT photos_owner_id_fkey
            FOREIGN KEY (owner_id)
            REFERENCES users (id)
                ON UPDATE NO ACTION
                ON DELETE CASCADE;

    """)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.execute("""
    ALTER TABLE invites
        DROP CONSTRAINT invites_sender_id_fkey,
        ADD CONSTRAINT invites_sender_id_fkey
            FOREIGN KEY (sender_id)
            REFERENCES users (id)
                ON UPDATE NO ACTION
                ON DELETE NO ACTION;

    ALTER TABLE tags
        DROP CONSTRAINT tags_owner_id_fkey,
        ADD CONSTRAINT tags_owner_id_fkey
            FOREIGN KEY (owner_id)
            REFERENCES users (id)
                ON UPDATE NO ACTION
                ON DELETE NO ACTION;

    ALTER TABLE photos
        DROP CONSTRAINT photos_owner_id_fkey,
        ADD CONSTRAINT photos_owner_id_fkey
            FOREIGN KEY (owner_id)
            REFERENCES users (id)
                ON UPDATE NO ACTION
                ON DELETE NO ACTION;

    """)

    ### end Alembic commands ###