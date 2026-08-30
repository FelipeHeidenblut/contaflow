"""add indexes for paginated operational queries

Revision ID: a6f2d8c4b190
Revises: e8b7c1d4a260
"""

from typing import Sequence, Union

from alembic import op


revision: str = "a6f2d8c4b190"
down_revision: Union[str, Sequence[str], None] = "e8b7c1d4a260"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_tasks_tenant_due_id",
            "tasks",
            ["tenant_id", "due_date", "id"],
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_tasks_tenant_client",
            "tasks",
            ["tenant_id", "client_id"],
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_tasks_tenant_assignee",
            "tasks",
            ["tenant_id", "assigned_to"],
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_documents_tenant_created_id",
            "documents",
            ["tenant_id", "created_at", "id"],
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_documents_tenant_client",
            "documents",
            ["tenant_id", "client_id"],
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_documents_tenant_client",
            table_name="documents",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_documents_tenant_created_id",
            table_name="documents",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_tasks_tenant_assignee",
            table_name="tasks",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_tasks_tenant_client",
            table_name="tasks",
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_tasks_tenant_due_id",
            table_name="tasks",
            postgresql_concurrently=True,
        )
