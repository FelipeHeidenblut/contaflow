"""move alert preferences to profiles

Revision ID: b7f2d9a4e610
Revises: a8e4c1d7b205
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b7f2d9a4e610"
down_revision: Union[str, Sequence[str], None] = "a8e4c1d7b205"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "profiles",
        sa.Column(
            "deadline_alerts_enabled",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.add_column(
        "profiles",
        sa.Column("alert_advance_hours", sa.Integer(), server_default="72", nullable=False),
    )
    op.create_check_constraint(
        "ck_profiles_alert_advance_hours",
        "profiles",
        "alert_advance_hours IN (48, 72, 168)",
    )

    op.add_column(
        "deadline_alerts",
        sa.Column("recipient_profile_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_deadline_alerts_recipient_profile_id",
        "deadline_alerts",
        "profiles",
        ["recipient_profile_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_deadline_alerts_recipient_profile_id",
        "deadline_alerts",
        ["recipient_profile_id"],
    )
    op.drop_constraint(
        "uq_deadline_alert_task_due_lead",
        "deadline_alerts",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_deadline_alert_task_due_lead_profile",
        "deadline_alerts",
        ["task_id", "due_date", "lead_hours", "recipient_profile_id"],
    )

    op.drop_constraint("ck_clients_alert_advance_hours", "clients", type_="check")
    op.drop_column("clients", "alert_advance_hours")
    op.drop_column("clients", "deadline_alerts_enabled")


def downgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("deadline_alerts_enabled", sa.Boolean(), server_default=sa.false(), nullable=False),
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

    op.drop_constraint(
        "uq_deadline_alert_task_due_lead_profile",
        "deadline_alerts",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_deadline_alert_task_due_lead",
        "deadline_alerts",
        ["task_id", "due_date", "lead_hours"],
    )
    op.drop_index("ix_deadline_alerts_recipient_profile_id", table_name="deadline_alerts")
    op.drop_constraint(
        "fk_deadline_alerts_recipient_profile_id",
        "deadline_alerts",
        type_="foreignkey",
    )
    op.drop_column("deadline_alerts", "recipient_profile_id")

    op.drop_constraint("ck_profiles_alert_advance_hours", "profiles", type_="check")
    op.drop_column("profiles", "alert_advance_hours")
    op.drop_column("profiles", "deadline_alerts_enabled")
