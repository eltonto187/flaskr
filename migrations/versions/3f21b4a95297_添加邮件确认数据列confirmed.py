"""添加邮件确认数据列confirmed

Revision ID: 3f21b4a95297
Revises: e52af527f9f5
Create Date: 2016-03-02 17:22:26.032425

"""

# revision identifiers, used by Alembic.
revision = '3f21b4a95297'
down_revision = 'e52af527f9f5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmed')
    ### end Alembic commands ###
