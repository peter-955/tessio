from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0022"
down_revision: str | None = "0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

QUARANTINE_EVENT_KINDS = ("quarantined", "released", "auto_released")


def upgrade() -> None:
    op.add_column("test_cases", sa.Column("flaky_score", sa.Integer(), server_default=sa.text("0"), nullable=False))
    op.add_column("test_cases", sa.Column("flaky_since", sa.DateTime(timezone=True), nullable=True))
    op.add_column("test_cases", sa.Column("disagreed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("test_cases", sa.Column("quarantined_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("test_cases", sa.Column("quarantined_by", sa.Uuid(), nullable=True))
    op.add_column("test_cases", sa.Column("quarantine_reason", sa.Text(), nullable=True))
    op.create_foreign_key("test_cases_quarantined_by_fkey", "test_cases", "users", ["quarantined_by"], ["id"])
    op.create_table(
        "test_case_quarantine_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("test_case_id", sa.Uuid(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                *QUARANTINE_EVENT_KINDS,
                name="quarantine_event_kind",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_test_case_quarantine_events_test_case_id_created_at",
        "test_case_quarantine_events",
        ["test_case_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_test_case_quarantine_events_test_case_id_created_at", table_name="test_case_quarantine_events")
    op.drop_table("test_case_quarantine_events")
    op.drop_constraint("test_cases_quarantined_by_fkey", "test_cases", type_="foreignkey")
    op.drop_column("test_cases", "quarantine_reason")
    op.drop_column("test_cases", "quarantined_by")
    op.drop_column("test_cases", "quarantined_at")
    op.drop_column("test_cases", "disagreed_at")
    op.drop_column("test_cases", "flaky_since")
    op.drop_column("test_cases", "flaky_score")
