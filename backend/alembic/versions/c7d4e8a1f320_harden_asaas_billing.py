"""Harden Asaas billing identities and webhook processing.

Revision ID: c7d4e8a1f320
Revises: b4e8c2f9a731
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "c7d4e8a1f320"
down_revision: Union[str, Sequence[str], None] = "b4e8c2f9a731"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "asaas_webhook_events",
        "status",
        existing_type=sa.String(length=20),
        existing_nullable=False,
        server_default="pending",
    )
    op.add_column(
        "tenants",
        sa.Column(
            "subscription_status",
            sa.String(length=30),
            server_default="none",
            nullable=False,
        ),
    )
    op.add_column(
        "tenants",
        sa.Column("billing_status_updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "billing_subscriptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("provider_customer_id", sa.String(length=100), nullable=False),
        sa.Column("provider_subscription_id", sa.String(length=100), nullable=True),
        sa.Column("external_reference", sa.String(length=180), nullable=False),
        sa.Column("plan_code", sa.String(length=30), nullable=True),
        sa.Column("billing_cycle", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("value", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("next_due_date", sa.Date(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint(
            "billing_cycle IN ('monthly', 'annual')",
            name="ck_billing_subscriptions_cycle",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "external_reference",
            name="uq_billing_subscriptions_external_reference",
        ),
        sa.UniqueConstraint("provider_subscription_id"),
    )
    op.create_index(
        "ix_billing_subscriptions_tenant_id",
        "billing_subscriptions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_billing_subscriptions_provider_customer_id",
        "billing_subscriptions",
        ["provider_customer_id"],
    )
    op.create_index(
        "ix_billing_subscriptions_provider_subscription_id",
        "billing_subscriptions",
        ["provider_subscription_id"],
    )
    op.create_index(
        "ix_billing_subscriptions_plan_code",
        "billing_subscriptions",
        ["plan_code"],
    )
    op.create_index(
        "ix_billing_subscriptions_status",
        "billing_subscriptions",
        ["status"],
    )

    op.create_table(
        "billing_reconciliation_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_events", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "processed_subscriptions", sa.Integer(), server_default="0", nullable=False
        ),
        sa.Column("processed_payments", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failures", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error", sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_billing_reconciliation_runs_started_at",
        "billing_reconciliation_runs",
        ["started_at"],
    )
    op.create_index(
        "ix_billing_reconciliation_runs_status",
        "billing_reconciliation_runs",
        ["status"],
    )

    op.execute(
        """
        INSERT INTO billing_subscriptions (
            id, tenant_id, provider_customer_id, provider_subscription_id,
            external_reference, plan_code, billing_cycle, status, value,
            created_at, updated_at
        )
        SELECT
            gen_random_uuid(), id, asaas_customer_id, asaas_subscription_id,
            'legacy:' || id::text || ':' || asaas_subscription_id,
            CASE WHEN plano IN ('basico', 'profissional', 'escritorio', 'business')
                THEN plano ELSE NULL END,
            CASE WHEN billing_cycle = 'annual' THEN 'annual' ELSE 'monthly' END,
            CASE status_pagamento
                WHEN 'ativo' THEN 'active'
                WHEN 'inadimplente' THEN 'overdue'
                WHEN 'cancelado' THEN 'canceled'
                ELSE 'pending'
            END,
            NULL, now(), now()
        FROM tenants
        WHERE asaas_subscription_id IS NOT NULL
          AND asaas_customer_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE tenants
        SET subscription_status = CASE status_pagamento
            WHEN 'ativo' THEN 'active'
            WHEN 'inadimplente' THEN 'overdue'
            WHEN 'cancelado' THEN 'canceled'
            ELSE 'pending'
        END
        WHERE asaas_subscription_id IS NOT NULL
        """
    )

    op.add_column(
        "asaas_webhook_events",
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "asaas_webhook_events",
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "asaas_webhook_events",
        sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "asaas_webhook_events",
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "asaas_webhook_events",
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_asaas_webhook_events_next_retry_at",
        "asaas_webhook_events",
        ["next_retry_at"],
    )

    for name, column in (
        ("provider_customer_id", sa.String(length=100)),
        ("external_reference", sa.String(length=180)),
        ("plan_code", sa.String(length=30)),
        ("billing_cycle", sa.String(length=20)),
        ("last_event_id", sa.String(length=100)),
    ):
        op.add_column("payment_records", sa.Column(name, column, nullable=True))
    op.add_column(
        "payment_records",
        sa.Column("provider_updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE payment_records AS payment
        SET provider_customer_id = tenant.asaas_customer_id,
            plan_code = CASE
                WHEN tenant.plano IN ('basico', 'profissional', 'escritorio', 'business')
                THEN tenant.plano ELSE NULL END,
            billing_cycle = CASE
                WHEN tenant.billing_cycle = 'annual' THEN 'annual' ELSE 'monthly' END
        FROM tenants AS tenant
        WHERE tenant.id = payment.tenant_id
        """
    )
    op.create_index(
        "ix_payment_records_subscription_id",
        "payment_records",
        ["subscription_id"],
    )
    op.create_index(
        "ix_payment_records_plan_code",
        "payment_records",
        ["plan_code"],
    )


def downgrade() -> None:
    op.drop_index("ix_payment_records_plan_code", table_name="payment_records")
    op.drop_index("ix_payment_records_subscription_id", table_name="payment_records")
    for name in (
        "provider_updated_at",
        "last_event_id",
        "billing_cycle",
        "plan_code",
        "external_reference",
        "provider_customer_id",
    ):
        op.drop_column("payment_records", name)

    op.drop_index(
        "ix_asaas_webhook_events_next_retry_at",
        table_name="asaas_webhook_events",
    )
    for name in (
        "next_retry_at",
        "processed_at",
        "processing_started_at",
        "attempts",
        "payload",
    ):
        op.drop_column("asaas_webhook_events", name)
    op.alter_column(
        "asaas_webhook_events",
        "status",
        existing_type=sa.String(length=20),
        existing_nullable=False,
        server_default="success",
    )

    op.drop_index(
        "ix_billing_reconciliation_runs_status",
        table_name="billing_reconciliation_runs",
    )
    op.drop_index(
        "ix_billing_reconciliation_runs_started_at",
        table_name="billing_reconciliation_runs",
    )
    op.drop_table("billing_reconciliation_runs")

    op.drop_index("ix_billing_subscriptions_status", table_name="billing_subscriptions")
    op.drop_index("ix_billing_subscriptions_plan_code", table_name="billing_subscriptions")
    op.drop_index(
        "ix_billing_subscriptions_provider_subscription_id",
        table_name="billing_subscriptions",
    )
    op.drop_index(
        "ix_billing_subscriptions_provider_customer_id",
        table_name="billing_subscriptions",
    )
    op.drop_index("ix_billing_subscriptions_tenant_id", table_name="billing_subscriptions")
    op.drop_table("billing_subscriptions")
    op.drop_column("tenants", "billing_status_updated_at")
    op.drop_column("tenants", "subscription_status")
