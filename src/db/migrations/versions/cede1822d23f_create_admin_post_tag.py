"""create admin, post, tag

Revision ID: cede1822d23f
Revises: 574c51ecb3ed
Create Date: 2022-02-02 10:13:42.572645

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'cede1822d23f'
down_revision = '574c51ecb3ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tag_post_map', 'tag_id',
               existing_type=mysql.CHAR(length=32),
               nullable=True)
    op.alter_column('tag_post_map', 'post_id',
               existing_type=mysql.CHAR(length=32),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tag_post_map', 'post_id',
               existing_type=mysql.CHAR(length=32),
               nullable=False)
    op.alter_column('tag_post_map', 'tag_id',
               existing_type=mysql.CHAR(length=32),
               nullable=False)
    # ### end Alembic commands ###