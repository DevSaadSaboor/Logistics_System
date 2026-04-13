"""add ivfflat cosine index

Revision ID: 87a63c4deefb
Revises: c693b4c23e3c
Create Date: 2026-04-12 17:27:57.002680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87a63c4deefb'
down_revision: Union[str, Sequence[str], None] = 'c693b4c23e3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    CREATE INDEX ix_shipments_embedding_ivfflat
    ON shipments
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
    """)


def downgrade():
    op.execute("""
    DROP INDEX ix_shipments_embedding_ivfflat;
    """)