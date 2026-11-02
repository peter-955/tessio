from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0016"
down_revision: str | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SUSPECTED_CAUSES = ("app_bug", "test_data", "environment", "test_case", "unknown")
FAILURE_EVENT_KINDS = ("opened", "failed_again", "status_changed", "assigned", "unassigned")
FAILURE_EVENT_KINDS_WITH_CAUSE = (*FAILURE_EVENT_KINDS, "cause_changed")


def build_enum(name: str, values: Sequence[str]) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, create_constraint=True, length=40)


def build_kind_check(values: Sequence[str]) -> str:
    return "kind IN ({})".format(", ".join(f"'{value}'" for value in values))


def upgrade() -> None:
    op.add_column("step_results", sa.Column("diagnosis", JSONB(none_as_null=True), nullable=True))
    op.add_column(
        "case_results",
        sa.Column("suspected_cause", build_enum("case_result_suspected_cause", SUSPECTED_CAUSES), nullable=True),
    )
    op.add_column("case_results", sa.Column("cause_reason", sa.Text(), nullable=True))
    op.add_column("failures", sa.Column("cause", build_enum("failure_cause", SUSPECTED_CAUSES), nullable=True))
    op.add_column("failures", sa.Column("cause_reason", sa.Text(), nullable=True))
    op.add_column("failures", sa.Column("cause_changed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("failures", sa.Column("cause_changed_by", sa.Uuid(), nullable=True))
    op.create_foreign_key("failures_cause_changed_by_fkey", "failures", "users", ["cause_changed_by"], ["id"])
    op.add_column(
        "failure_events",
        sa.Column("from_cause", build_enum("failure_event_from_cause", SUSPECTED_CAUSES), nullable=True),
    )
    op.add_column(
        "failure_events",
        sa.Column("to_cause", build_enum("failure_event_to_cause", SUSPECTED_CAUSES), nullable=True),
    )
    op.drop_constraint("failure_event_kind", "failure_events", type_="check")
    op.create_check_constraint("failure_event_kind", "failure_events", build_kind_check(FAILURE_EVENT_KINDS_WITH_CAUSE))


def downgrade() -> None:
    op.execute("DELETE FROM failure_events WHERE kind = 'cause_changed'")
    op.drop_constraint("failure_event_kind", "failure_events", type_="check")
    op.create_check_constraint("failure_event_kind", "failure_events", build_kind_check(FAILURE_EVENT_KINDS))
    op.drop_column("failure_events", "to_cause")
    op.drop_column("failure_events", "from_cause")
    op.drop_constraint("failures_cause_changed_by_fkey", "failures", type_="foreignkey")
    op.drop_column("failures", "cause_changed_by")
    op.drop_column("failures", "cause_changed_at")
    op.drop_column("failures", "cause_reason")
    op.drop_column("failures", "cause")
    op.drop_column("case_results", "cause_reason")
    op.drop_column("case_results", "suspected_cause")
    op.drop_column("step_results", "diagnosis")
