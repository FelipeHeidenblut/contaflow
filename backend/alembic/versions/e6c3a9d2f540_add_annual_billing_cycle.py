"""add annual billing cycle

Revision ID: e6c3a9d2f540
Revises: d2b5f7a8c410
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e6c3a9d2f540"
down_revision: Union[str, Sequence[str], None] = "d2b5f7a8c410"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenants",
        sa.Column(
            "billing_cycle",
            sa.String(length=20),
            server_default="monthly",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("tenants", "billing_cycle")
