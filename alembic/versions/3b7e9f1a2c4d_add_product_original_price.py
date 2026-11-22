"""add original_price to products

Revision ID: 3b7e9f1a2c4d
Revises: 16ad2546c68c
Create Date: 2026-11-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '3b7e9f1a2c4d'
down_revision: Union[str, Sequence[str], None] = '16ad2546c68c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('products', sa.Column('original_price', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'original_price')
