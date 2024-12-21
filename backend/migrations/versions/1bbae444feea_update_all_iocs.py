"""update all_iocs

Revision ID: 1bbae444feea
Revises: efee3a71ad7e
Create Date: 2024-12-06 14:54:36.022423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bbae444feea'
down_revision: Union[str, None] = 'efee3a71ad7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('all_iocs', 'category')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('all_iocs', sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###