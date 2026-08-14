"""add admin analytics, payments and audit

Revision ID: d2b5f7a8c410
Revises: c9a4e6f1b320
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d2b5f7a8c410"
down_revision: Union[str, Sequence[str], None] = "c9a4e6f1b320"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("asaas_webhook_events", sa.Column("tenant_id", sa.UUID(), nullable=True))
    op.add_column(
        "asaas_webhook_events",
        sa.Column("status", sa.String(length=20), server_default="success", nullable=False),
    )
    op.add_column(
        "asaas_webhook_events", sa.Column("error", sa.String(length=1000), nullable=True)
    )
    op.create_foreign_key(
        "fk_asaas_webhook_events_tenant_id",
        "asaas_webhook_events",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_asaas_webhook_events_tenant_id", "asaas_webhook_events", ["tenant_id"]
    )
    op.create_index(
        "ix_asaas_webhook_events_status", "asaas_webhook_events", ["status"]
    )

    op.create_table(
        "payment_records",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("provider_payment_id", sa.String(length=100), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("subscription_id", sa.String(length=100), nullable=True),
        sa.Column("value", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invoice_url", sa.String(length=500), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_payment_id"),
    )
    op.create_index("ix_payment_records_tenant_id", "payment_records", ["tenant_id"])
    op.create_index("ix_payment_records_status", "payment_records", ["status"])
    op.create_index("ix_payment_records_paid_at", "payment_records", ["paid_at"])

    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("actor_profile_id", sa.UUID(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("old_value", sa.String(length=100), nullable=True),
        sa.Column("new_value", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["actor_profile_id"], ["profiles.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_admin_audit_logs_tenant_id", "admin_audit_logs", ["tenant_id"])
    op.create_index(
        "ix_admin_audit_logs_actor_profile_id",
        "admin_audit_logs",
        ["actor_profile_id"],
    )
    op.create_index("ix_admin_audit_logs_created_at", "admin_audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_admin_audit_logs_created_at", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_actor_profile_id", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_tenant_id", table_name="admin_audit_logs")
    op.drop_table("admin_audit_logs")

    op.drop_index("ix_payment_records_paid_at", table_name="payment_records")
    op.drop_index("ix_payment_records_status", table_name="payment_records")
    op.drop_index("ix_payment_records_tenant_id", table_name="payment_records")
    op.drop_table("payment_records")

    op.drop_index("ix_asaas_webhook_events_status", table_name="asaas_webhook_events")
    op.drop_index("ix_asaas_webhook_events_tenant_id", table_name="asaas_webhook_events")
    op.drop_constraint(
        "fk_asaas_webhook_events_tenant_id",
        "asaas_webhook_events",
        type_="foreignkey",
    )
    op.drop_column("asaas_webhook_events", "error")
    op.drop_column("asaas_webhook_events", "status")
    op.drop_column("asaas_webhook_events", "tenant_id")
