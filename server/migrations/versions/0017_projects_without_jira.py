from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0017"
down_revision: str | None = "0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("projects", "jira_project_key", existing_type=sa.String(), nullable=True)
    op.alter_column("projects", "jira_board_id", existing_type=sa.Integer(), nullable=True)
    op.add_column(
        "stories",
        sa.Column(
            "source",
            sa.Enum("jira", "tessio", name="story_source", native_enum=False, create_constraint=True, length=40),
            server_default="jira",
            nullable=False,
        ),
    )
    op.create_table(
        "story_key_counters",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("last_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("project_id"),
    )


def downgrade() -> None:
    op.drop_table("story_key_counters")
    op.drop_column("stories", "source")
    op.alter_column("projects", "jira_board_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("projects", "jira_project_key", existing_type=sa.String(), nullable=False)
