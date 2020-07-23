"""empty message

Revision ID: 101a83d34ec4
Revises: 
Create Date: 2020-07-20 21:11:05.340072

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2.types import Geography


# revision identifiers, used by Alembic.
revision = '101a83d34ec4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('trails',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('route', Geography(geometry_type='MULTILINESTRING', from_text='ST_GeogFromText', name='geography'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trails')
    # ### end Alembic commands ###