from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FAILURE_STATUSES = ("open", "fixed", "verified", "reopened")
FAILURE_EVENT_KINDS = ("opened", "failed_again", "status_changed", "assigned", "unassigned")


def build_enum(name: str, values: Sequence[str]) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, create_constraint=True, length=40)


def upgrade() -> None:
    op.create_table(
        "failures",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("story_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("opened_by_case_result_id", sa.Uuid(), nullable=False),
        sa.Column("latest_case_result_id", sa.Uuid(), nullable=False),
        sa.Column("assignee_id", sa.Uuid(), nullable=True),
        sa.Column("status", build_enum("failure_status", FAILURE_STATUSES), nullable=False),
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status_changed_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"]),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.ForeignKeyConstraint(["opened_by_case_result_id"], ["case_results.id"]),
        sa.ForeignKeyConstraint(["latest_case_result_id"], ["case_results.id"]),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["status_changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_failures_project_id"), "failures", ["project_id"], unique=False)
    op.create_index(op.f("ix_failures_story_id"), "failures", ["story_id"], unique=False)
    op.create_index(op.f("ix_failures_assignee_id"), "failures", ["assignee_id"], unique=False)
    op.create_index(
        "uq_failures_test_case_id_active",
        "failures",
        ["test_case_id"],
        unique=True,
        postgresql_where=sa.text("status <> 'verified'"),
    )
    op.create_table(
        "failure_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("failure_id", sa.Uuid(), nullable=False),
        sa.Column("kind", build_enum("failure_event_kind", FAILURE_EVENT_KINDS), nullable=False),
        sa.Column("from_status", build_enum("failure_event_from_status", FAILURE_STATUSES), nullable=True),
        sa.Column("to_status", build_enum("failure_event_to_status", FAILURE_STATUSES), nullable=True),
        sa.Column("case_result_id", sa.Uuid(), nullable=True),
        sa.Column("assignee_id", sa.Uuid(), nullable=True),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["failure_id"], ["failures.id"]),
        sa.ForeignKeyConstraint(["case_result_id"], ["case_results.id"]),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_failure_events_failure_id"), "failure_events", ["failure_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_failure_events_failure_id"), table_name="failure_events")
    op.drop_table("failure_events")
    op.drop_index(
        "uq_failures_test_case_id_active", table_name="failures", postgresql_where=sa.text("status <> 'verified'")
    )
    op.drop_index(op.f("ix_failures_assignee_id"), table_name="failures")
    op.drop_index(op.f("ix_failures_story_id"), table_name="failures")
    op.drop_index(op.f("ix_failures_project_id"), table_name="failures")
    op.drop_table("failures")
