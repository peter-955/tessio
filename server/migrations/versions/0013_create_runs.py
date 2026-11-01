from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RESULT_STATUSES = ("passed", "failed", "blocked", "skipped")


def build_enum(name: str, values: Sequence[str]) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, create_constraint=True, length=40)


def upgrade() -> None:
    op.create_table(
        "runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("story_id", sa.Uuid(), nullable=False),
        sa.Column("environment_id", sa.Uuid(), nullable=False),
        sa.Column("executor", build_enum("run_executor", ("claude", "manual")), nullable=False),
        sa.Column("status", build_enum("run_status", ("running", "passed", "failed", "aborted")), nullable=False),
        sa.Column("abort_reason", build_enum("run_abort_reason", ("no_results", "inactive")), nullable=True),
        sa.Column("parent_run_id", sa.Uuid(), nullable=True),
        sa.Column("started_by", sa.Uuid(), nullable=False),
        sa.Column("started_via_token_id", sa.Uuid(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("report", postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"]),
        sa.ForeignKeyConstraint(["environment_id"], ["environments.id"]),
        sa.ForeignKeyConstraint(["parent_run_id"], ["runs.id"]),
        sa.ForeignKeyConstraint(["started_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_runs_project_id"), "runs", ["project_id"], unique=False)
    op.create_index(op.f("ix_runs_story_id"), "runs", ["story_id"], unique=False)
    op.create_index(op.f("ix_runs_environment_id"), "runs", ["environment_id"], unique=False)
    op.create_index(op.f("ix_runs_parent_run_id"), "runs", ["parent_run_id"], unique=False)
    op.create_index(
        "uq_runs_story_id_running", "runs", ["story_id"], unique=True, postgresql_where=sa.text("status = 'running'")
    )
    op.create_index("ix_runs_project_id_started_at", "runs", ["project_id", "started_at"], unique=False)
    op.create_index("ix_runs_status_last_activity_at", "runs", ["status", "last_activity_at"], unique=False)
    op.create_table(
        "run_cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_version_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"]),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.ForeignKeyConstraint(["test_case_version_id"], ["test_case_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "test_case_id"),
    )
    op.create_table(
        "case_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_version_id", sa.Uuid(), nullable=False),
        sa.Column("status", build_enum("case_result_status", RESULT_STATUSES), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("recorded_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"]),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.ForeignKeyConstraint(["test_case_version_id"], ["test_case_versions.id"]),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "test_case_id"),
    )
    op.create_index(
        "ix_case_results_test_case_id_created_at", "case_results", ["test_case_id", "created_at"], unique=False
    )
    op.create_table(
        "step_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_result_id", sa.Uuid(), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("status", build_enum("step_result_status", RESULT_STATUSES), nullable=False),
        sa.Column("actual_result", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("screenshot_file_id", sa.Uuid(), nullable=True),
        sa.Column("evidence_file_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["case_result_id"], ["case_results.id"]),
        sa.ForeignKeyConstraint(["screenshot_file_id"], ["stored_files.id"]),
        sa.ForeignKeyConstraint(["evidence_file_id"], ["stored_files.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_result_id", "step_order"),
    )
    op.create_table(
        "run_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("test_file_version_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("requested_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"]),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.ForeignKeyConstraint(["test_file_version_id"], ["test_file_versions.id"]),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "test_case_id", "key"),
    )


def downgrade() -> None:
    op.drop_table("run_files")
    op.drop_table("step_results")
    op.drop_index("ix_case_results_test_case_id_created_at", table_name="case_results")
    op.drop_table("case_results")
    op.drop_table("run_cases")
    op.drop_index("ix_runs_status_last_activity_at", table_name="runs")
    op.drop_index("ix_runs_project_id_started_at", table_name="runs")
    op.drop_index("uq_runs_story_id_running", table_name="runs", postgresql_where=sa.text("status = 'running'"))
    op.drop_index(op.f("ix_runs_parent_run_id"), table_name="runs")
    op.drop_index(op.f("ix_runs_environment_id"), table_name="runs")
    op.drop_index(op.f("ix_runs_story_id"), table_name="runs")
    op.drop_index(op.f("ix_runs_project_id"), table_name="runs")
    op.drop_table("runs")
