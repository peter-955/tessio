from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sprints",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("jira_sprint_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "state",
            sa.Enum(
                "active",
                "future",
                "closed",
                name="sprint_state",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("complete_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "jira_sprint_id"),
    )
    op.create_index(op.f("ix_sprints_project_id"), "sprints", ["project_id"], unique=False)
    op.create_table(
        "stories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("sprint_id", sa.Uuid(), nullable=True),
        sa.Column("jira_id", sa.String(), nullable=False),
        sa.Column("jira_key", sa.String(), nullable=False),
        sa.Column("jira_url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), nullable=True),
        sa.Column("jira_status", sa.String(), nullable=False),
        sa.Column("jira_issue_type", sa.String(), nullable=False),
        sa.Column(
            "test_status",
            sa.Enum(
                "not_started",
                "ready_for_test",
                "in_test",
                "passed",
                "failed",
                name="story_test_status",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("test_status_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("test_status_changed_by", sa.Uuid(), nullable=True),
        sa.Column("jira_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("jira_missing_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["sprint_id"], ["sprints.id"]),
        sa.ForeignKeyConstraint(["test_status_changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "jira_id"),
        sa.UniqueConstraint("project_id", "jira_key"),
    )
    op.create_index(op.f("ix_stories_project_id"), "stories", ["project_id"], unique=False)
    op.create_index(op.f("ix_stories_sprint_id"), "stories", ["sprint_id"], unique=False)
    op.create_table(
        "acceptance_criteria",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("story_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("story_id", "position"),
    )
    op.create_table(
        "project_sync_states",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "never",
                "queued",
                "running",
                "succeeded",
                "failed",
                name="project_sync_status",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("requested_by", sa.Uuid(), nullable=True),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_succeeded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("project_id"),
    )


def downgrade() -> None:
    op.drop_table("project_sync_states")
    op.drop_table("acceptance_criteria")
    op.drop_index(op.f("ix_stories_sprint_id"), table_name="stories")
    op.drop_index(op.f("ix_stories_project_id"), table_name="stories")
    op.drop_table("stories")
    op.drop_index(op.f("ix_sprints_project_id"), table_name="sprints")
    op.drop_table("sprints")
