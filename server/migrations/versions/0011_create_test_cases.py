from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "test_case_counters",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("last_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("project_id"),
    )
    op.create_table(
        "test_cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("story_id", sa.Uuid(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column(
            "priority",
            sa.Enum(
                "critical",
                "high",
                "medium",
                "low",
                name="test_case_priority",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "in_review",
                "ready",
                "deprecated",
                name="test_case_status",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("current_version_id", sa.Uuid(), nullable=True),
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status_changed_by", sa.Uuid(), nullable=True),
        sa.Column("needs_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("needs_review_criterion_ids", postgresql.ARRAY(sa.Uuid()), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.Uuid(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"]),
        sa.ForeignKeyConstraint(["status_changed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "number"),
    )
    op.create_index(op.f("ix_test_cases_story_id"), "test_cases", ["story_id"], unique=False)
    op.create_table(
        "test_case_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column(
            "priority",
            sa.Enum(
                "critical",
                "high",
                "medium",
                "low",
                name="test_case_version_priority",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("business_value", sa.Text(), nullable=True),
        sa.Column("preconditions", sa.Text(), nullable=True),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("criterion_ids", postgresql.ARRAY(sa.Uuid()), nullable=False),
        sa.Column("data_keys", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("file_version_ids", postgresql.ARRAY(sa.Uuid()), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_case_id", "number"),
    )
    op.create_foreign_key(
        "test_cases_current_version_id_fkey",
        "test_cases",
        "test_case_versions",
        ["current_version_id"],
        ["id"],
    )
    op.create_table(
        "test_case_criteria",
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("criterion_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.ForeignKeyConstraint(["criterion_id"], ["acceptance_criteria.id"]),
        sa.PrimaryKeyConstraint("test_case_id", "criterion_id"),
    )
    op.create_index(op.f("ix_test_case_criteria_criterion_id"), "test_case_criteria", ["criterion_id"], unique=False)
    op.create_table(
        "test_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("current_version_id", sa.Uuid(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_case_id", "key"),
    )
    op.create_index(op.f("ix_test_files_project_id"), "test_files", ["project_id"], unique=False)
    op.create_table(
        "test_file_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("test_file_id", sa.Uuid(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("stored_file_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["test_file_id"], ["test_files.id"]),
        sa.ForeignKeyConstraint(["stored_file_id"], ["stored_files.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_file_id"),
        sa.UniqueConstraint("test_file_id", "number"),
    )
    op.create_foreign_key(
        "test_files_current_version_id_fkey",
        "test_files",
        "test_file_versions",
        ["current_version_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("test_files_current_version_id_fkey", "test_files", type_="foreignkey")
    op.drop_constraint("test_cases_current_version_id_fkey", "test_cases", type_="foreignkey")
    op.drop_table("test_file_versions")
    op.drop_index(op.f("ix_test_files_project_id"), table_name="test_files")
    op.drop_table("test_files")
    op.drop_index(op.f("ix_test_case_criteria_criterion_id"), table_name="test_case_criteria")
    op.drop_table("test_case_criteria")
    op.drop_table("test_case_versions")
    op.drop_index(op.f("ix_test_cases_story_id"), table_name="test_cases")
    op.drop_table("test_cases")
    op.drop_table("test_case_counters")
