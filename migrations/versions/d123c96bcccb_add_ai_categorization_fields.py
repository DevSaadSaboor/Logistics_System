"""add ai categorization fields

Revision ID: d123c96bcccb
Revises: e751eef839fc
Create Date: 2026-04-01 22:58:34.878027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd123c96bcccb'
down_revision: Union[str, Sequence[str], None] = 'e751eef839fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: add as nullable
    op.add_column('shipments', sa.Column('category', sa.String(length=50), nullable=True))
    op.add_column('shipments', sa.Column('confidence', sa.Float(), nullable=True))

    # Step 2: fill existing rows
    op.execute("UPDATE shipments SET category = 'other'")
    op.execute("UPDATE shipments SET confidence = 0.0")

    # Step 3: enforce NOT NULL
    op.alter_column('shipments', 'category', nullable=False)
    op.alter_column('shipments', 'confidence', nullable=False)

def downgrade() -> None:
    op.drop_column('shipments', 'confidence')
    op.drop_column('shipments', 'category')
