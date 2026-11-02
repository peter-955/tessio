from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0026"
down_revision: str | None = "0025"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMPTY_JSON_ARRAY = sa.text("'[]'::jsonb")
CASE_RESULT_KEY = "case_results_run_id_test_case_id_key"
CASE_RESULT_ITERATION_KEY = "case_results_run_id_test_case_id_iteration_key"
CURRENT_VERSION_FOREIGN_KEY = "shared_steps_current_version_id_fkey"


def upgrade() -> None:
    op.create_table(
        "shared_steps",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("current_version_id", sa.Uuid(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "key"),
    )
    op.create_index(op.f("ix_shared_steps_project_id"), "shared_steps", ["project_id"], unique=False)
    op.create_table(
        "shared_step_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("shared_step_id", sa.Uuid(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("data_keys", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["shared_step_id"], ["shared_steps.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("shared_step_id", "number"),
    )
    op.create_foreign_key(
        CURRENT_VERSION_FOREIGN_KEY,
        "shared_steps",
        "shared_step_versions",
        ["current_version_id"],
        ["id"],
    )
    op.add_column(
        "test_case_versions",
        sa.Column(
            "parameters",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=EMPTY_JSON_ARRAY,
            nullable=False,
        ),
    )
    op.add_column(
        "test_case_versions",
        sa.Column(
            "data_rows",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=EMPTY_JSON_ARRAY,
            nullable=False,
        ),
    )
    op.add_column("run_cases", sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("case_results", sa.Column("iteration", sa.Integer(), server_default=sa.text("0"), nullable=False))
    op.drop_constraint(CASE_RESULT_KEY, "case_results", type_="unique")
    op.create_unique_constraint(CASE_RESULT_ITERATION_KEY, "case_results", ["run_id", "test_case_id", "iteration"])


def downgrade() -> None:
    op.execute("DELETE FROM step_results WHERE case_result_id IN (SELECT id FROM case_results WHERE iteration > 0)")
    op.execute("DELETE FROM case_results WHERE iteration > 0")
    op.drop_constraint(CASE_RESULT_ITERATION_KEY, "case_results", type_="unique")
    op.create_unique_constraint(CASE_RESULT_KEY, "case_results", ["run_id", "test_case_id"])
    op.drop_column("case_results", "iteration")
    op.drop_column("run_cases", "steps")
    op.drop_column("test_case_versions", "data_rows")
    op.drop_column("test_case_versions", "parameters")
    op.drop_constraint(CURRENT_VERSION_FOREIGN_KEY, "shared_steps", type_="foreignkey")
    op.drop_table("shared_step_versions")
    op.drop_index(op.f("ix_shared_steps_project_id"), table_name="shared_steps")
    op.drop_table("shared_steps")
