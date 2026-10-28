"""Keep completed tasks in history while hiding them from the operational lists."""
from alembic import op
import sqlalchemy as sa

revision = "b7c4e2a9d615"
down_revision = "f2d8a1b6c903"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tasks", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    op.create_check_constraint(
        "ck_tasks_archived_completed", "tasks", "archived_at IS NULL OR status = 'concluida'"
    )
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_tasks_tenant_archived_due_id", "tasks",
            ["tenant_id", "archived_at", "due_date", "id"],
            postgresql_concurrently=True,
        )


def downgrade():
    with op.get_context().autocommit_block():
        op.drop_index("ix_tasks_tenant_archived_due_id", table_name="tasks", postgresql_concurrently=True)
    op.drop_constraint("ck_tasks_archived_completed", "tasks", type_="check")
    op.drop_column("tasks", "archived_at")
