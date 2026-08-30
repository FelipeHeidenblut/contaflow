"""Make monthly task recurrence idempotent.

Revision ID: b4e8c2f9a731
Revises: f1a7c4e9b260
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b4e8c2f9a731"
down_revision: Union[str, Sequence[str], None] = "f1a7c4e9b260"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks", sa.Column("recurrence_series_id", sa.UUID(), nullable=True)
    )
    op.add_column("tasks", sa.Column("recurrence_period", sa.Date(), nullable=True))
    op.add_column(
        "tasks", sa.Column("next_occurrence_id", sa.UUID(), nullable=True)
    )
    op.add_column(
        "tasks",
        sa.Column("recurrence_processed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.execute("UPDATE tasks SET is_recurring = false WHERE is_recurring IS NULL")
    op.execute(
        """
        UPDATE tasks
        SET recurrence_day = EXTRACT(DAY FROM due_date)::integer
        WHERE is_recurring = true
          AND (recurrence_day IS NULL OR recurrence_day NOT BETWEEN 1 AND 31)
        """
    )
    op.execute(
        """
        UPDATE tasks
        SET recurrence_series_id = gen_random_uuid(),
            recurrence_period = CASE
                -- O motor antigo já salvava o vencimento ajustado. Quando um
                -- dia alto atravessou o fim de semana para o começo do mês,
                -- a competência real é o mês anterior.
                WHEN recurrence_day > EXTRACT(DAY FROM due_date)::integer
                    AND EXTRACT(DAY FROM due_date)::integer <= 3
                THEN date_trunc('month', due_date - INTERVAL '1 month')::date
                ELSE date_trunc('month', due_date)::date
            END
        WHERE is_recurring = true
        """
    )
    # Historical completed tasks may already have generated children that cannot
    # be linked reliably. Marking them avoids creating surprise duplicates.
    op.execute(
        """
        UPDATE tasks
        SET recurrence_processed_at = now()
        WHERE is_recurring = true AND status = 'concluida'
        """
    )

    op.alter_column(
        "tasks",
        "is_recurring",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.false(),
    )
    op.create_check_constraint(
        "ck_tasks_recurrence_day",
        "tasks",
        "recurrence_day IS NULL OR recurrence_day BETWEEN 1 AND 31",
    )
    op.create_check_constraint(
        "ck_tasks_recurring_identity",
        "tasks",
        "NOT is_recurring OR (recurrence_day IS NOT NULL "
        "AND recurrence_series_id IS NOT NULL AND recurrence_period IS NOT NULL)",
    )
    op.create_check_constraint(
        "ck_tasks_recurrence_period_month",
        "tasks",
        "recurrence_period IS NULL OR "
        "recurrence_period = date_trunc('month', recurrence_period)::date",
    )
    op.create_unique_constraint(
        "uq_tasks_tenant_series_period",
        "tasks",
        ["tenant_id", "recurrence_series_id", "recurrence_period"],
    )
    op.create_foreign_key(
        "fk_tasks_next_occurrence_id",
        "tasks",
        "tasks",
        ["next_occurrence_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_tasks_recurrence_series_id",
        "tasks",
        ["recurrence_series_id"],
    )
    op.create_index(
        "ix_tasks_next_occurrence_id",
        "tasks",
        ["next_occurrence_id"],
    )

    op.create_table(
        "recurrence_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "processed_tasks",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "created_tasks", sa.Integer(), server_default="0", nullable=False
        ),
        sa.Column("error", sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recurrence_runs_started_at", "recurrence_runs", ["started_at"])
    op.create_index("ix_recurrence_runs_status", "recurrence_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_recurrence_runs_status", table_name="recurrence_runs")
    op.drop_index("ix_recurrence_runs_started_at", table_name="recurrence_runs")
    op.drop_table("recurrence_runs")

    op.drop_index("ix_tasks_next_occurrence_id", table_name="tasks")
    op.drop_index("ix_tasks_recurrence_series_id", table_name="tasks")
    op.drop_constraint("fk_tasks_next_occurrence_id", "tasks", type_="foreignkey")
    op.drop_constraint(
        "uq_tasks_tenant_series_period", "tasks", type_="unique"
    )
    op.drop_constraint(
        "ck_tasks_recurrence_period_month", "tasks", type_="check"
    )
    op.drop_constraint("ck_tasks_recurring_identity", "tasks", type_="check")
    op.drop_constraint("ck_tasks_recurrence_day", "tasks", type_="check")
    op.alter_column(
        "tasks",
        "is_recurring",
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
    )
    op.drop_column("tasks", "recurrence_processed_at")
    op.drop_column("tasks", "next_occurrence_id")
    op.drop_column("tasks", "recurrence_period")
    op.drop_column("tasks", "recurrence_series_id")
