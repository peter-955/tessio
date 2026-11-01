from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jira_connection",
        sa.Column("id", sa.SmallInteger(), autoincrement=False, nullable=False),
        sa.Column("site_url", sa.Text(), nullable=False),
        sa.Column("account_email", sa.Text(), nullable=False),
        sa.Column("api_token_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("account_id", sa.Text(), nullable=False),
        sa.Column("account_display_name", sa.Text(), nullable=False),
        sa.Column("configured_by", sa.Uuid(), nullable=False),
        sa.Column("configured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_jira_connection_singleton"),
        sa.ForeignKeyConstraint(["configured_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("jira_connection")
