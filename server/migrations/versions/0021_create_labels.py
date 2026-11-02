from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0021"
down_revision: str | None = "0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LABEL_COLORS = ("gray", "red", "orange", "yellow", "green", "teal", "blue", "violet")


def upgrade() -> None:
    op.create_table(
        "labels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "color",
            sa.Enum(*LABEL_COLORS, name="label_color", native_enum=False, create_constraint=True, length=40),
            nullable=False,
        ),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name"),
    )
    op.create_index(op.f("ix_labels_project_id"), "labels", ["project_id"], unique=False)
    op.create_table(
        "test_case_labels",
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column("label_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["label_id"], ["labels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.PrimaryKeyConstraint("test_case_id", "label_id"),
    )
    op.create_index(op.f("ix_test_case_labels_label_id"), "test_case_labels", ["label_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_test_case_labels_label_id"), table_name="test_case_labels")
    op.drop_table("test_case_labels")
    op.drop_index(op.f("ix_labels_project_id"), table_name="labels")
    op.drop_table("labels")
