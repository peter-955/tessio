from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gaps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("story_id", sa.Uuid(), nullable=False),
        sa.Column(
            "target_type",
            sa.Enum(
                "story",
                "criterion",
                "test_case",
                name="gap_target_type",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("target_id", sa.Uuid(), nullable=True),
        sa.Column(
            "type",
            sa.Enum(
                "missing_ac",
                "unclear_goal",
                "missing_step",
                "missing_test_data",
                "other",
                name="gap_type",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column(
            "data_scope",
            sa.Enum(
                "project",
                "environment",
                name="gap_data_scope",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=True,
        ),
        sa.Column(
            "severity",
            sa.Enum(
                "high",
                "medium",
                "low",
                name="gap_severity",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "open",
                "resolved",
                name="gap_status",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("assignee_id", sa.Uuid(), nullable=True),
        sa.Column(
            "assignee_role",
            sa.Enum(
                "admin",
                "pm",
                "ba",
                "qc",
                "dev",
                "viewer",
                name="gap_assignee_role",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=True,
        ),
        sa.Column("raised_by", sa.Uuid(), nullable=False),
        sa.Column("raised_via_token_id", sa.Uuid(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("answered_by", sa.Uuid(), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reopened_by", sa.Uuid(), nullable=True),
        sa.Column("reopened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"]),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["raised_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["answered_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["reopened_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_gaps_project_id"), "gaps", ["project_id"], unique=False)
    op.create_index(op.f("ix_gaps_assignee_id"), "gaps", ["assignee_id"], unique=False)
    op.create_index("ix_gaps_story_id_status", "gaps", ["story_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_gaps_story_id_status", table_name="gaps")
    op.drop_index(op.f("ix_gaps_assignee_id"), table_name="gaps")
    op.drop_index(op.f("ix_gaps_project_id"), table_name="gaps")
    op.drop_table("gaps")
