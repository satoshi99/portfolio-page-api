"""empty message

Revision ID: 88c3f4b920bd
Revises: 0e9026993af2
Create Date: 2022-02-09 22:50:33.855399

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '88c3f4b920bd'
down_revision = '0e9026993af2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admins', sa.Column('email_verified', sa.Boolean(), nullable=False))
    op.add_column('admins', sa.Column('salt', sa.String(length=255), nullable=False))
    op.add_column('admins', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('admins', sa.Column('is_superuser', sa.Boolean(), nullable=False))
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
    op.drop_column('admins', 'is_superuser')
    op.drop_column('admins', 'is_active')
    op.drop_column('admins', 'salt')
    op.drop_column('admins', 'email_verified')
    # ### end Alembic commands ###
