"""enable pgvector extension

Revision ID: 000000000000
Revises: 
Create Date: 2026-05-10 00:00:00.000000

NOTE: This migration must run BEFORE the initial schema migration.
      On Supabase, pgvector is pre-installed — this just activates it.
"""
from typing import Sequence, Union
from alembic import op


# revision identifiers
revision: str = '000000000000'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enable the pgvector extension (safe to run multiple times)."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    """Drop the pgvector extension."""
    op.execute("DROP EXTENSION IF EXISTS vector;")
