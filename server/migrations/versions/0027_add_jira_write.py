from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision: str = "0027"
down_revision: str | None = "0026"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

JIRA_POST_RESULTS = ("off", "on_sign_off", "every_run")
FAILURE_EVENT_KINDS = ("opened", "failed_again", "status_changed", "assigned", "unassigned", "cause_changed")
FAILURE_EVENT_KINDS_WITH_JIRA = (*FAILURE_EVENT_KINDS, "jira_issue_created", "jira_issue_failed")


def build_kind_check(values: Sequence[str]) -> str:
    return "kind IN ({})".format(", ".join(f"'{value}'" for value in values))


def upgrade() -> None:
    op.add_column("failures", sa.Column("jira_issue_key", sa.Text(), nullable=True))
    op.add_column("failures", sa.Column("jira_issue_url", sa.Text(), nullable=True))
    op.add_column("failures", sa.Column("jira_issue_status", sa.Text(), nullable=True))
    op.add_column("failures", sa.Column("jira_issue_done_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("failures", sa.Column("jira_issue_requested_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("failures", sa.Column("jira_issue_error_code", sa.String(length=40), nullable=True))
    op.add_column("failure_events", sa.Column("jira_issue_key", sa.Text(), nullable=True))
    op.add_column("failure_events", sa.Column("error_code", sa.String(length=40), nullable=True))
    op.drop_constraint("failure_event_kind", "failure_events", type_="check")
    op.create_check_constraint("failure_event_kind", "failure_events", build_kind_check(FAILURE_EVENT_KINDS_WITH_JIRA))
    op.add_column(
        "projects", sa.Column("jira_bug_issue_type", sa.Text(), server_default=sa.text("'Bug'"), nullable=False)
    )
    op.add_column(
        "projects",
        sa.Column(
            "jira_post_results",
            sa.Enum(*JIRA_POST_RESULTS, name="jira_post_results", native_enum=False, create_constraint=True, length=40),
            server_default=sa.text("'off'"),
            nullable=False,
        ),
    )
    op.add_column("jira_connection", sa.Column("can_create_issues", sa.Boolean(), nullable=True))
    op.add_column("jira_connection", sa.Column("can_comment", sa.Boolean(), nullable=True))
    op.add_column(
        "jira_connection",
        sa.Column("missing_permissions", ARRAY(sa.Text()), server_default=sa.text("'{}'"), nullable=False),
    )
    op.add_column("jira_connection", sa.Column("permissions_checked_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("jira_connection", "permissions_checked_at")
    op.drop_column("jira_connection", "missing_permissions")
    op.drop_column("jira_connection", "can_comment")
    op.drop_column("jira_connection", "can_create_issues")
    op.drop_column("projects", "jira_post_results")
    op.drop_column("projects", "jira_bug_issue_type")
    op.execute("DELETE FROM failure_events WHERE kind IN ('jira_issue_created', 'jira_issue_failed')")
    op.drop_constraint("failure_event_kind", "failure_events", type_="check")
    op.create_check_constraint("failure_event_kind", "failure_events", build_kind_check(FAILURE_EVENT_KINDS))
    op.drop_column("failure_events", "error_code")
    op.drop_column("failure_events", "jira_issue_key")
    op.drop_column("failures", "jira_issue_error_code")
    op.drop_column("failures", "jira_issue_requested_at")
    op.drop_column("failures", "jira_issue_done_at")
    op.drop_column("failures", "jira_issue_status")
    op.drop_column("failures", "jira_issue_url")
    op.drop_column("failures", "jira_issue_key")
