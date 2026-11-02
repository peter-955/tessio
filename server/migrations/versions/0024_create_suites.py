from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0024"
down_revision: str | None = "0023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RUN_EXECUTORS = ("claude", "manual")
RUN_EXECUTORS_WITH_SCRIPT_AND_CI = ("claude", "manual", "script", "ci")
NOTIFICATION_KINDS = ("gap_assigned", "failure_assigned", "run_finished")
NOTIFICATION_KINDS_WITH_SUITE_RUN = ("gap_assigned", "failure_assigned", "run_finished", "suite_run_finished")
RUNNING_RUN_PER_SUITE_INDEX = "uq_runs_test_suite_id_running"
ACTIVE_SUITE_NAME_INDEX = "uq_test_suites_project_id_name_active"
STORY_OR_SUITE_CHECK = "ck_runs_story_or_suite"
DELETE_SUITE_RUN_STATEMENTS = (
    "CREATE TEMPORARY TABLE suite_run_ids AS SELECT id FROM runs WHERE test_suite_id IS NOT NULL",
    "CREATE TEMPORARY TABLE suite_case_result_ids AS "
    "SELECT id FROM case_results WHERE run_id IN (SELECT id FROM suite_run_ids)",
    "CREATE TEMPORARY TABLE suite_failure_ids AS "
    "SELECT id FROM failures WHERE opened_by_case_result_id IN (SELECT id FROM suite_case_result_ids)",
    "DELETE FROM notifications WHERE kind = 'suite_run_finished' OR (kind = 'failure_assigned' "
    "AND payload->>'failure_id' IN (SELECT id::text FROM suite_failure_ids))",
    "DELETE FROM failure_events WHERE failure_id IN (SELECT id FROM suite_failure_ids)",
    "DELETE FROM failures WHERE id IN (SELECT id FROM suite_failure_ids)",
    "UPDATE failures SET latest_case_result_id = COALESCE("
    "(SELECT failure_events.case_result_id FROM failure_events "
    "JOIN case_results ON case_results.id = failure_events.case_result_id "
    "WHERE failure_events.failure_id = failures.id "
    "AND case_results.id NOT IN (SELECT id FROM suite_case_result_ids) "
    "ORDER BY case_results.created_at DESC LIMIT 1), opened_by_case_result_id) "
    "WHERE latest_case_result_id IN (SELECT id FROM suite_case_result_ids)",
    "UPDATE failure_events SET case_result_id = NULL WHERE case_result_id IN (SELECT id FROM suite_case_result_ids)",
    "DELETE FROM step_results WHERE case_result_id IN (SELECT id FROM suite_case_result_ids)",
    "DELETE FROM case_results WHERE id IN (SELECT id FROM suite_case_result_ids)",
    "DELETE FROM run_cases WHERE run_id IN (SELECT id FROM suite_run_ids)",
    "DELETE FROM run_files WHERE run_id IN (SELECT id FROM suite_run_ids)",
    "DELETE FROM run_log_entries WHERE run_id IN (SELECT id FROM suite_run_ids)",
    "DELETE FROM run_logs WHERE run_id IN (SELECT id FROM suite_run_ids)",
    "UPDATE runs SET parent_run_id = NULL WHERE parent_run_id IN (SELECT id FROM suite_run_ids)",
    "DELETE FROM runs WHERE id IN (SELECT id FROM suite_run_ids)",
    "DROP TABLE suite_failure_ids, suite_case_result_ids, suite_run_ids",
)


def build_value_check(column: str, values: Sequence[str]) -> str:
    quoted_values = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({quoted_values})"


def upgrade() -> None:
    op.create_table(
        "test_suites",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_suites_project_id"), "test_suites", ["project_id"], unique=False)
    op.create_index(
        ACTIVE_SUITE_NAME_INDEX,
        "test_suites",
        ["project_id", sa.text("lower(name)")],
        unique=True,
        postgresql_where=sa.text("archived_at IS NULL"),
    )
    op.create_table(
        "test_suite_cases",
        sa.Column("test_suite_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.ForeignKeyConstraint(["test_suite_id"], ["test_suites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("test_suite_id", "test_case_id"),
    )
    op.create_index(op.f("ix_test_suite_cases_test_case_id"), "test_suite_cases", ["test_case_id"], unique=False)
    op.alter_column("runs", "story_id", existing_type=sa.Uuid(), nullable=True)
    op.add_column("runs", sa.Column("test_suite_id", sa.Uuid(), nullable=True))
    op.add_column("runs", sa.Column("skipped_cases", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_foreign_key("runs_test_suite_id_fkey", "runs", "test_suites", ["test_suite_id"], ["id"])
    op.create_index(op.f("ix_runs_test_suite_id"), "runs", ["test_suite_id"], unique=False)
    op.create_index(
        RUNNING_RUN_PER_SUITE_INDEX,
        "runs",
        ["test_suite_id"],
        unique=True,
        postgresql_where=sa.text("status = 'running'"),
    )
    op.create_check_constraint(STORY_OR_SUITE_CHECK, "runs", "(story_id IS NULL) <> (test_suite_id IS NULL)")
    op.drop_constraint("run_executor", "runs", type_="check")
    op.create_check_constraint("run_executor", "runs", build_value_check("executor", RUN_EXECUTORS_WITH_SCRIPT_AND_CI))
    op.drop_constraint("notification_kind", "notifications", type_="check")
    op.create_check_constraint(
        "notification_kind", "notifications", build_value_check("kind", NOTIFICATION_KINDS_WITH_SUITE_RUN)
    )


def downgrade() -> None:
    for statement in DELETE_SUITE_RUN_STATEMENTS:
        op.execute(sa.text(statement))
    op.drop_constraint("notification_kind", "notifications", type_="check")
    op.create_check_constraint("notification_kind", "notifications", build_value_check("kind", NOTIFICATION_KINDS))
    op.drop_constraint("run_executor", "runs", type_="check")
    op.create_check_constraint("run_executor", "runs", build_value_check("executor", RUN_EXECUTORS))
    op.drop_constraint(STORY_OR_SUITE_CHECK, "runs", type_="check")
    op.drop_index(RUNNING_RUN_PER_SUITE_INDEX, table_name="runs", postgresql_where=sa.text("status = 'running'"))
    op.drop_index(op.f("ix_runs_test_suite_id"), table_name="runs")
    op.drop_constraint("runs_test_suite_id_fkey", "runs", type_="foreignkey")
    op.drop_column("runs", "skipped_cases")
    op.drop_column("runs", "test_suite_id")
    op.alter_column("runs", "story_id", existing_type=sa.Uuid(), nullable=False)
    op.drop_index(op.f("ix_test_suite_cases_test_case_id"), table_name="test_suite_cases")
    op.drop_table("test_suite_cases")
    op.drop_index(ACTIVE_SUITE_NAME_INDEX, table_name="test_suites", postgresql_where=sa.text("archived_at IS NULL"))
    op.drop_index(op.f("ix_test_suites_project_id"), table_name="test_suites")
    op.drop_table("test_suites")
