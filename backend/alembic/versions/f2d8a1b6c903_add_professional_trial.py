"""Add opt-in-at-registration professional trial dates; existing offices unchanged."""
from alembic import op
import sqlalchemy as sa

revision = "f2d8a1b6c903"
down_revision = "a6f2d8c4b190"
branch_labels = None
depends_on = None


def upgrade():
    for name in ("trial_started_at", "trial_ends_at", "trial_converted_at"):
        op.add_column("tenants", sa.Column(name, sa.DateTime(timezone=True), nullable=True))


def downgrade():
    for name in ("trial_converted_at", "trial_ends_at", "trial_started_at"):
        op.drop_column("tenants", name)
