"""add chat history

Revision ID: 093b8ac6bbd3
Revises: 51d71267be31
Create Date: 2026-05-06 14:03:55.901863

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "093b8ac6bbd3"
down_revision: Union[str, Sequence[str], None] = "51d71267be31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_history",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True
        ),

        sa.Column(
            "session_id",
            sa.String(),
            nullable=False,
            index=True
        ),

        sa.Column(
            "role",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "content",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table("chat_history")