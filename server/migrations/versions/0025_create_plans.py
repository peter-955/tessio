from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0025"
down_revision: str | None = "0024"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PLAN_STATUSES = ("open", "signed_off", "closed")
SUITE_OR_STORY_CHECK = "ck_test_plan_items_suite_or_story"


def upgrade() -> None:
    op.create_table(
        "test_plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("environment_id", sa.Uuid(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(*PLAN_STATUSES, name="test_plan_status", native_enum=False, create_constraint=True, length=40),
            nullable=False,
        ),
        sa.Column("signed_off_by", sa.Uuid(), nullable=True),
        sa.Column("signed_off_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by", sa.Uuid(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["closed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["environment_id"], ["environments.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["signed_off_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_plans_project_id"), "test_plans", ["project_id"], unique=False)
    op.create_table(
        "test_plan_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("test_plan_id", sa.Uuid(), nullable=False),
        sa.Column("test_suite_id", sa.Uuid(), nullable=True),
        sa.Column("story_id", sa.Uuid(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("(test_suite_id IS NULL) <> (story_id IS NULL)", name=SUITE_OR_STORY_CHECK),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"]),
        sa.ForeignKeyConstraint(["test_plan_id"], ["test_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_suite_id"], ["test_suites.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_plan_id", "story_id"),
        sa.UniqueConstraint("test_plan_id", "test_suite_id"),
    )
    op.create_index(op.f("ix_test_plan_items_test_plan_id"), "test_plan_items", ["test_plan_id"], unique=False)
    op.create_index(op.f("ix_test_plan_items_story_id"), "test_plan_items", ["story_id"], unique=False)
    op.create_index(op.f("ix_test_plan_items_test_suite_id"), "test_plan_items", ["test_suite_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_test_plan_items_test_suite_id"), table_name="test_plan_items")
    op.drop_index(op.f("ix_test_plan_items_story_id"), table_name="test_plan_items")
    op.drop_index(op.f("ix_test_plan_items_test_plan_id"), table_name="test_plan_items")
    op.drop_table("test_plan_items")
    op.drop_index(op.f("ix_test_plans_project_id"), table_name="test_plans")
    op.drop_table("test_plans")
