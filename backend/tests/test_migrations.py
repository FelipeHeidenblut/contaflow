import os
import subprocess
import sys
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.config import Config
from alembic.script import ScriptDirectory


BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
EXPECTED_TABLES = {
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
}
EXPECTED_SECURED_TABLES = EXPECTED_TABLES
EXPECTED_COLUMNS = {
    "tenants": {
        "asaas_customer_id",
        "billing_cycle",
        "plano",
        "status_pagamento",
        "subscription_status",
        "billing_status_updated_at",
    },
    "profiles": {"is_superadmin", "deadline_alerts_enabled", "calendar_token"},
    "clients": {"natureza_operacao", "responsible_profile_id", "email"},
    "tasks": {
        "is_recurring",
        "recurrence_day",
        "grau_importancia",
        "recurrence_series_id",
        "recurrence_period",
        "next_occurrence_id",
        "recurrence_processed_at",
    },
    "asaas_webhook_events": {
        "payload",
        "attempts",
        "processing_started_at",
        "processed_at",
        "next_retry_at",
    },
    "payment_records": {
        "provider_customer_id",
        "external_reference",
        "plan_code",
        "billing_cycle",
        "last_event_id",
        "provider_updated_at",
    },
    "billing_subscriptions": {
        "provider_customer_id",
        "provider_subscription_id",
        "external_reference",
        "plan_code",
        "billing_cycle",
        "status",
        "last_synced_at",
    },
    "billing_reconciliation_runs": {
        "processed_events",
        "processed_subscriptions",
        "processed_payments",
        "failures",
    },
}

EXPECTED_OPERATIONAL_INDEXES = {
    "tasks": {
        "ix_tasks_tenant_due_id",
        "ix_tasks_tenant_client",
        "ix_tasks_tenant_assignee",
    },
    "documents": {
        "ix_documents_tenant_created_id",
        "ix_documents_tenant_client",
    },
}


def _alembic_config() -> Config:
    config = Config(ALEMBIC_INI)
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return config


def test_migration_history_has_one_base_and_one_head():
    script = ScriptDirectory.from_config(_alembic_config())

    assert script.get_base() == "452ebc16bf35"
    assert script.get_current_head() == "a6f2d8c4b190"


def test_full_history_compiles_for_an_empty_postgresql_database():
    env = os.environ.copy()
    env["DATABASE_URL"] = (
        "postgresql://migration_test:migration_test@localhost/migration_test"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(ALEMBIC_INI),
            "upgrade",
            "head",
            "--sql",
        ],
        cwd=BACKEND_DIR,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    sql = result.stdout
    for table_name in EXPECTED_TABLES:
        assert f"CREATE TABLE {table_name}" in sql
    assert "ADD COLUMN asaas_customer_id" in sql
    assert "ADD COLUMN is_superadmin" in sql
    assert "ADD COLUMN natureza_operacao" in sql
    assert "ADD COLUMN is_recurring" in sql
    assert "ADD COLUMN recurrence_series_id" in sql
    assert "uq_tasks_tenant_series_period" in sql
    assert "CREATE TABLE billing_subscriptions" in sql
    assert "ADD COLUMN payload JSONB" in sql
    for index_names in EXPECTED_OPERATIONAL_INDEXES.values():
        for index_name in index_names:
            assert f"CREATE INDEX CONCURRENTLY {index_name}" in sql
    for table_name in EXPECTED_SECURED_TABLES:
        assert f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY' in sql
        assert f'REVOKE ALL PRIVILEGES ON TABLE "{table_name}"' in sql


def test_upgrade_head_on_disposable_empty_postgresql_database():
    """Live smoke test; opt in with a dedicated, empty PostgreSQL database."""
    database_url = os.getenv("MIGRATION_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("MIGRATION_TEST_DATABASE_URL não configurada")
    if database_url == os.getenv("DATABASE_URL"):
        pytest.fail("MIGRATION_TEST_DATABASE_URL não pode ser igual a DATABASE_URL")

    engine = sa.create_engine(database_url)
    with engine.connect() as connection:
        existing_tables = set(sa.inspect(connection).get_table_names())
    if existing_tables:
        pytest.fail(
            "MIGRATION_TEST_DATABASE_URL deve apontar para um banco vazio; "
            f"tabelas encontradas: {sorted(existing_tables)}"
        )

    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(ALEMBIC_INI),
            "upgrade",
            "head",
        ],
        cwd=BACKEND_DIR,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    with engine.connect() as connection:
        inspector = sa.inspect(connection)
        assert EXPECTED_TABLES <= set(inspector.get_table_names())
        for table_name, expected_columns in EXPECTED_COLUMNS.items():
            actual_columns = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            assert expected_columns <= actual_columns

        for table_name, expected_indexes in EXPECTED_OPERATIONAL_INDEXES.items():
            actual_indexes = {
                index["name"] for index in inspector.get_indexes(table_name)
            }
            assert expected_indexes <= actual_indexes

        rls_rows = connection.execute(
            sa.text(
                """
                SELECT c.relname, c.relrowsecurity
                FROM pg_class AS c
                JOIN pg_namespace AS n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public'
                  AND c.relname = ANY(:table_names)
                """
            ),
            {"table_names": sorted(EXPECTED_SECURED_TABLES)},
        )
        rls_by_table = {name: enabled for name, enabled in rls_rows}
        assert rls_by_table == {
            table_name: True for table_name in EXPECTED_SECURED_TABLES
        }

        current_revision = connection.execute(
            sa.text("SELECT version_num FROM alembic_version")
        ).scalar_one()
        assert current_revision == "a6f2d8c4b190"
