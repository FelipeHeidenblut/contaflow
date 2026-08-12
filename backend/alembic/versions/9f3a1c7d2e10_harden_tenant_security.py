"""Harden tenant relationships, calendar feeds and Asaas webhooks.

Revision ID: 9f3a1c7d2e10
Revises: d543a3bf9f08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9f3a1c7d2e10"
down_revision: Union[str, Sequence[str], None] = "d543a3bf9f08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("calendar_token", sa.String(length=64), nullable=True))
    op.add_column("tenants", sa.Column("asaas_subscription_id", sa.String(), nullable=True))
    op.create_index("ix_tenants_calendar_token", "tenants", ["calendar_token"], unique=True)
    op.create_unique_constraint(
        "uq_tenants_asaas_subscription_id", "tenants", ["asaas_subscription_id"]
    )

    # A criação das constraints falha de forma segura se houver duplicidades legadas;
    # nenhum CPF/CNPJ é alterado silenciosamente pela migração.
    op.create_foreign_key(
        "fk_clients_tenant_id", "clients", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE"
    )
    op.create_unique_constraint("uq_clients_tenant_cnpj", "clients", ["tenant_id", "cnpj"])
    op.create_unique_constraint("uq_clients_tenant_cpf", "clients", ["tenant_id", "cpf"])

    op.create_table(
        "asaas_webhook_events",
        sa.Column("id", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("asaas_webhook_events")
    op.drop_constraint("uq_clients_tenant_cpf", "clients", type_="unique")
    op.drop_constraint("uq_clients_tenant_cnpj", "clients", type_="unique")
    op.drop_constraint("fk_clients_tenant_id", "clients", type_="foreignkey")
    op.drop_constraint("uq_tenants_asaas_subscription_id", "tenants", type_="unique")
    op.drop_index("ix_tenants_calendar_token", table_name="tenants")
    op.drop_column("tenants", "asaas_subscription_id")
    op.drop_column("tenants", "calendar_token")
