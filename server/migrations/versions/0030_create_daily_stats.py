from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0030"
down_revision: str | None = "0029"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOTIFICATION_KINDS = ("gap_assigned", "failure_assigned", "run_finished", "suite_run_finished")
NOTIFICATION_KINDS_WITH_REPORT_READY = (*NOTIFICATION_KINDS, "report_ready")


def build_value_check(column: str, values: Sequence[str]) -> str:
    quoted_values = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({quoted_values})"


def upgrade() -> None:
    op.create_table(
        "project_daily_stats",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("runs_by_executor", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("passed_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("blocked_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("failures_opened", sa.Integer(), nullable=False),
        sa.Column("failures_fixed", sa.Integer(), nullable=False),
        sa.Column("fix_seconds_total", sa.BigInteger(), nullable=False),
        sa.Column("gaps_opened", sa.Integer(), nullable=False),
        sa.Column("gaps_answered", sa.Integer(), nullable=False),
        sa.Column("answer_seconds_total", sa.BigInteger(), nullable=False),
        sa.Column("open_gap_count", sa.Integer(), nullable=False),
        sa.Column("median_open_gap_age_seconds", sa.BigInteger(), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("project_id", "day"),
    )
    op.drop_constraint("notification_kind", "notifications", type_="check")
    op.create_check_constraint(
        "notification_kind", "notifications", build_value_check("kind", NOTIFICATION_KINDS_WITH_REPORT_READY)
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM notifications WHERE kind = 'report_ready'"))
    op.drop_constraint("notification_kind", "notifications", type_="check")
    op.create_check_constraint("notification_kind", "notifications", build_value_check("kind", NOTIFICATION_KINDS))
    op.drop_table("project_daily_stats")
