"""add client portfolios, managers and comments

Revision ID: c9a4e6f1b320
Revises: b7f2d9a4e610
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9a4e6f1b320"
down_revision: Union[str, Sequence[str], None] = "b7f2d9a4e610"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE profiles SET role = 'colaborador' WHERE role IS NULL OR role = 'user'")
    op.add_column("profiles", sa.Column("calendar_token", sa.String(length=64), nullable=True))
    op.create_index("ix_profiles_calendar_token", "profiles", ["calendar_token"], unique=True)

    op.add_column(
        "clients", sa.Column("responsible_profile_id", sa.UUID(), nullable=True)
    )
    op.create_foreign_key(
        "fk_clients_responsible_profile_id",
        "clients",
        "profiles",
        ["responsible_profile_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_clients_responsible_profile_id",
        "clients",
        ["responsible_profile_id"],
    )

    op.create_table(
        "comments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("client_id", sa.UUID(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=True),
        sa.Column("author_id", sa.UUID(), nullable=True),
        sa.Column("content", sa.String(length=2000), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comments_tenant_id", "comments", ["tenant_id"])
    op.create_index("ix_comments_client_id", "comments", ["client_id"])
    op.create_index("ix_comments_task_id", "comments", ["task_id"])
    op.create_index("ix_comments_author_id", "comments", ["author_id"])


def downgrade() -> None:
    op.drop_index("ix_comments_author_id", table_name="comments")
    op.drop_index("ix_comments_task_id", table_name="comments")
    op.drop_index("ix_comments_client_id", table_name="comments")
    op.drop_index("ix_comments_tenant_id", table_name="comments")
    op.drop_table("comments")

    op.drop_index("ix_clients_responsible_profile_id", table_name="clients")
    op.drop_constraint(
        "fk_clients_responsible_profile_id", "clients", type_="foreignkey"
    )
    op.drop_column("clients", "responsible_profile_id")

    op.drop_index("ix_profiles_calendar_token", table_name="profiles")
    op.drop_column("profiles", "calendar_token")
