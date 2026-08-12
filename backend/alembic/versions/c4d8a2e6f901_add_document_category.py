"""add document category

Revision ID: c4d8a2e6f901
Revises: 9f3a1c7d2e10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4d8a2e6f901"
down_revision: Union[str, Sequence[str], None] = "9f3a1c7d2e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("categoria", sa.String(length=40), server_default="Geral", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("documents", "categoria")
