"""Normalize columns previously created outside Alembic.

Revision ID: f1a7c4e9b260
Revises: e6c3a9d2f540

Some columns were added to SQLAlchemy models while environments were still
being prepared with ``create_all`` or manual SQL. This reconciliation revision
adds only columns that are absent, so it is safe both for a database created
from the full migration chain and for an existing stamped database.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import context, op


revision: str = "f1a7c4e9b260"
down_revision: Union[str, Sequence[str], None] = "e6c3a9d2f540"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table_name: str) -> set[str]:
    if context.is_offline_mode():
        return set()
    return {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def _add_if_missing(table_name: str, column: sa.Column) -> None:
    if column.name not in _columns(table_name):
        op.add_column(table_name, column)


def upgrade() -> None:
    _add_if_missing(
        "tenants", sa.Column("asaas_customer_id", sa.String(), nullable=True)
    )
    _add_if_missing("tenants", sa.Column("plano", sa.String(), nullable=True))
    _add_if_missing(
        "tenants", sa.Column("status_pagamento", sa.String(), nullable=True)
    )

    _add_if_missing(
        "profiles",
        sa.Column(
            "is_superadmin",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )

    _add_if_missing(
        "clients", sa.Column("natureza_operacao", sa.String(), nullable=True)
    )

    _add_if_missing("tasks", sa.Column("is_recurring", sa.Boolean(), nullable=True))
    _add_if_missing("tasks", sa.Column("recurrence_day", sa.Integer(), nullable=True))
    _add_if_missing(
        "tasks", sa.Column("grau_importancia", sa.String(), nullable=True)
    )


def downgrade() -> None:
    # These columns may predate Alembic in legacy databases. Dropping them on a
    # downgrade could destroy application data, so this reconciliation is
    # intentionally irreversible.
    pass
