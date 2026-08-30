"""Lock down application tables exposed through the Supabase Data API.

Revision ID: e8b7c1d4a260
Revises: c7d4e8a1f320
"""

from typing import Sequence, Union

from alembic import op


revision: str = "e8b7c1d4a260"
down_revision: Union[str, Sequence[str], None] = "c7d4e8a1f320"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


APPLICATION_TABLES = (
    "admin_audit_logs",
    "asaas_webhook_events",
    "billing_reconciliation_runs",
    "billing_subscriptions",
    "clients",
    "comments",
    "deadline_alerts",
    "documents",
    "payment_records",
    "profiles",
    "recurrence_runs",
    "tasks",
    "tax_deadlines",
    "tenants",
)


def _revoke_if_role_exists(table_name: str, role_name: str) -> None:
    op.execute(
        f"""
        DO $do$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role_name}') THEN
                EXECUTE 'REVOKE ALL PRIVILEGES ON TABLE "{table_name}" FROM {role_name}';
            END IF;
        END
        $do$;
        """
    )


def upgrade() -> None:
    for table_name in APPLICATION_TABLES:
        op.execute(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY')
        _revoke_if_role_exists(table_name, "anon")
        _revoke_if_role_exists(table_name, "authenticated")


def downgrade() -> None:
    raise RuntimeError(
        "O hardening de RLS é irreversível; reverta apenas o código da aplicação."
    )
