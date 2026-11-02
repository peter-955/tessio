from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0015"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("UPDATE test_data SET kind = 'variable' WHERE kind = 'endpoint'")
    op.drop_constraint("data_item_kind", "test_data", type_="check")
    op.create_check_constraint("data_item_kind", "test_data", "kind IN ('variable', 'secret')")
    op.create_table(
        "test_data_descriptions",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("project_id", "key"),
    )


def downgrade() -> None:
    op.drop_table("test_data_descriptions")
    op.drop_constraint("data_item_kind", "test_data", type_="check")
    op.create_check_constraint("data_item_kind", "test_data", "kind IN ('variable', 'endpoint', 'secret')")
