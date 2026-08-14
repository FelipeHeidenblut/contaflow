"""add deadline email alerts

Revision ID: a8e4c1d7b205
Revises: c4d8a2e6f901
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a8e4c1d7b205"
down_revision: Union[str, Sequence[str], None] = "c4d8a2e6f901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("email", sa.String(length=320), nullable=True))
    op.add_column(
        "clients",
        sa.Column(
            "deadline_alerts_enabled",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.add_column(
        "clients",
        sa.Column("alert_advance_hours", sa.Integer(), server_default="72", nullable=False),
    )
    op.create_check_constraint(
        "ck_clients_alert_advance_hours",
        "clients",
        "alert_advance_hours IN (48, 72, 168)",
    )

    op.create_table(
        "deadline_alerts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("client_id", sa.UUID(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("lead_hours", sa.Integer(), nullable=False),
        sa.Column("recipient_email", sa.String(length=320), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="processing", nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="1", nullable=False),
        sa.Column("last_error", sa.String(length=1000), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "task_id",
            "due_date",
            "lead_hours",
            name="uq_deadline_alert_task_due_lead",
        ),
    )
    op.create_index("ix_deadline_alerts_tenant_id", "deadline_alerts", ["tenant_id"])
    op.create_index("ix_deadline_alerts_client_id", "deadline_alerts", ["client_id"])
    op.create_index("ix_deadline_alerts_task_id", "deadline_alerts", ["task_id"])


def downgrade() -> None:
    op.drop_index("ix_deadline_alerts_task_id", table_name="deadline_alerts")
    op.drop_index("ix_deadline_alerts_client_id", table_name="deadline_alerts")
    op.drop_index("ix_deadline_alerts_tenant_id", table_name="deadline_alerts")
    op.drop_table("deadline_alerts")
    op.drop_constraint("ck_clients_alert_advance_hours", "clients", type_="check")
    op.drop_column("clients", "alert_advance_hours")
    op.drop_column("clients", "deadline_alerts_enabled")
    op.drop_column("clients", "email")
