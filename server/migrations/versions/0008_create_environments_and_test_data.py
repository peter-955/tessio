from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "environments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("health_check_url", sa.Text(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name"),
    )
    op.create_index(op.f("ix_environments_project_id"), "environments", ["project_id"], unique=False)
    op.create_table(
        "test_data",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("environment_id", sa.Uuid(), nullable=True),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "variable",
                "endpoint",
                "secret",
                name="data_item_kind",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("value_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["environment_id"], ["environments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id", "environment_id", "key", name="uq_test_data_scope_key", postgresql_nulls_not_distinct=True
        ),
    )
    op.create_index(op.f("ix_test_data_project_id"), "test_data", ["project_id"], unique=False)
    op.create_index(op.f("ix_test_data_environment_id"), "test_data", ["environment_id"], unique=False)
    op.add_column("projects", sa.Column("default_environment_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_projects_default_environment_id",
        "projects",
        "environments",
        ["default_environment_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_projects_default_environment_id", "projects", type_="foreignkey")
    op.drop_column("projects", "default_environment_id")
    op.drop_index(op.f("ix_test_data_environment_id"), table_name="test_data")
    op.drop_index(op.f("ix_test_data_project_id"), table_name="test_data")
    op.drop_table("test_data")
    op.drop_index(op.f("ix_environments_project_id"), table_name="environments")
    op.drop_table("environments")
