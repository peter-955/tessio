from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0029"
down_revision: str | None = "0028"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

API_TOKEN_SCOPES = ("mcp", "api")
WEBHOOK_EVENTS = (
    "run.started",
    "run.finished",
    "failure.opened",
    "failure.status_changed",
    "gap.raised",
    "story.signed_off",
    "plan.signed_off",
)
WEBHOOK_DELIVERY_STATUSES = ("pending", "succeeded", "failed")
WEBHOOK_EVENT_VALUES = ", ".join(f"'{event}'" for event in WEBHOOK_EVENTS)
STORY_OR_SUITE_CHECK = "ck_runs_story_or_suite"
STORY_OR_SUITE_CONDITION = "(story_id IS NULL) <> (test_suite_id IS NULL)"
STORY_OR_SUITE_OR_CI_CONDITION = (
    "((story_id IS NULL) <> (test_suite_id IS NULL)) "
    "OR (executor = 'ci' AND story_id IS NULL AND test_suite_id IS NULL)"
)
DELETE_UNTARGETED_CI_RUN_STATEMENTS = (
    "CREATE TEMPORARY TABLE ci_run_ids AS SELECT id FROM runs "
    "WHERE executor = 'ci' AND story_id IS NULL AND test_suite_id IS NULL",
    "CREATE TEMPORARY TABLE ci_case_result_ids AS "
    "SELECT id FROM case_results WHERE run_id IN (SELECT id FROM ci_run_ids)",
    "CREATE TEMPORARY TABLE ci_failure_ids AS "
    "SELECT id FROM failures WHERE opened_by_case_result_id IN (SELECT id FROM ci_case_result_ids)",
    "DELETE FROM notifications WHERE kind = 'failure_assigned' "
    "AND payload->>'failure_id' IN (SELECT id::text FROM ci_failure_ids)",
    "DELETE FROM failure_events WHERE failure_id IN (SELECT id FROM ci_failure_ids)",
    "DELETE FROM failures WHERE id IN (SELECT id FROM ci_failure_ids)",
    "UPDATE failures SET latest_case_result_id = COALESCE("
    "(SELECT failure_events.case_result_id FROM failure_events "
    "JOIN case_results ON case_results.id = failure_events.case_result_id "
    "WHERE failure_events.failure_id = failures.id "
    "AND case_results.id NOT IN (SELECT id FROM ci_case_result_ids) "
    "ORDER BY case_results.created_at DESC LIMIT 1), opened_by_case_result_id) "
    "WHERE latest_case_result_id IN (SELECT id FROM ci_case_result_ids)",
    "UPDATE failure_events SET case_result_id = NULL WHERE case_result_id IN (SELECT id FROM ci_case_result_ids)",
    "DELETE FROM step_results WHERE case_result_id IN (SELECT id FROM ci_case_result_ids)",
    "DELETE FROM case_results WHERE id IN (SELECT id FROM ci_case_result_ids)",
    "DELETE FROM run_cases WHERE run_id IN (SELECT id FROM ci_run_ids)",
    "DELETE FROM run_files WHERE run_id IN (SELECT id FROM ci_run_ids)",
    "DELETE FROM run_log_entries WHERE run_id IN (SELECT id FROM ci_run_ids)",
    "DELETE FROM run_logs WHERE run_id IN (SELECT id FROM ci_run_ids)",
    "UPDATE runs SET parent_run_id = NULL WHERE parent_run_id IN (SELECT id FROM ci_run_ids)",
    "DELETE FROM runs WHERE id IN (SELECT id FROM ci_run_ids)",
    "DROP TABLE ci_failure_ids, ci_case_result_ids, ci_run_ids",
)


def build_value_check(column: str, values: Sequence[str]) -> str:
    quoted_values = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({quoted_values})"


def upgrade() -> None:
    op.add_column(
        "api_tokens",
        sa.Column("scope", sa.String(length=40), server_default=sa.text("'mcp'"), nullable=False),
    )
    op.create_check_constraint("api_token_scope", "api_tokens", build_value_check("scope", API_TOKEN_SCOPES))
    op.create_table(
        "webhooks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("secret_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("events", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            f"cardinality(events) > 0 AND events <@ ARRAY[{WEBHOOK_EVENT_VALUES}]::text[]", name="webhook_events"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhooks_project_id"), "webhooks", ["project_id"], unique=False)
    op.create_table(
        "webhook_deliveries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("webhook_id", sa.Uuid(), nullable=False),
        sa.Column("event", sa.String(length=40), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("redelivery_of_id", sa.Uuid(), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(build_value_check("event", WEBHOOK_EVENTS), name="webhook_event"),
        sa.CheckConstraint(build_value_check("status", WEBHOOK_DELIVERY_STATUSES), name="webhook_delivery_status"),
        sa.ForeignKeyConstraint(["redelivery_of_id"], ["webhook_deliveries.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["webhook_id"], ["webhooks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_webhook_deliveries_webhook_id_created_at", "webhook_deliveries", ["webhook_id", "created_at"], unique=False
    )
    op.create_index(op.f("ix_webhook_deliveries_created_at"), "webhook_deliveries", ["created_at"], unique=False)
    op.drop_constraint(STORY_OR_SUITE_CHECK, "runs", type_="check")
    op.create_check_constraint(STORY_OR_SUITE_CHECK, "runs", STORY_OR_SUITE_OR_CI_CONDITION)


def downgrade() -> None:
    for statement in DELETE_UNTARGETED_CI_RUN_STATEMENTS:
        op.execute(sa.text(statement))
    op.drop_constraint(STORY_OR_SUITE_CHECK, "runs", type_="check")
    op.create_check_constraint(STORY_OR_SUITE_CHECK, "runs", STORY_OR_SUITE_CONDITION)
    op.drop_index(op.f("ix_webhook_deliveries_created_at"), table_name="webhook_deliveries")
    op.drop_index("ix_webhook_deliveries_webhook_id_created_at", table_name="webhook_deliveries")
    op.drop_table("webhook_deliveries")
    op.drop_index(op.f("ix_webhooks_project_id"), table_name="webhooks")
    op.drop_table("webhooks")
    op.drop_constraint("api_token_scope", "api_tokens", type_="check")
    op.drop_column("api_tokens", "scope")
