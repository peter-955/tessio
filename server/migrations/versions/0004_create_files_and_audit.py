from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stored_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column(
            "kind",
            sa.Enum(
                "screenshot",
                "test_file",
                "evidence",
                "import",
                "avatar",
                "report",
                name="stored_file_kind",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("object_key", sa.Text(), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("content_type", sa.Text(), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=True),
        sa.Column("sha256", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "uploaded",
                "missing",
                name="stored_file_status",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("uploaded_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("object_key"),
    )
    op.create_index(op.f("ix_stored_files_project_id"), "stored_files", ["project_id"], unique=False)
    op.create_index(op.f("ix_stored_files_uploaded_by"), "stored_files", ["uploaded_by"], unique=False)
    op.create_index("ix_stored_files_status_created_at", "stored_files", ["status", "created_at"], unique=False)
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("api_token_id", sa.Uuid(), nullable=True),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column(
            "action",
            sa.Enum(
                "secret.reveal",
                "secret.resolve",
                name="audit_action",
                native_enum=False,
                create_constraint=True,
                length=40,
            ),
            nullable=False,
        ),
        sa.Column("target_id", sa.Uuid(), nullable=True),
        sa.Column("run_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_events_actor_id"), "audit_events", ["actor_id"], unique=False)
    op.create_index("ix_audit_events_project_id_created_at", "audit_events", ["project_id", "created_at"], unique=False)
    op.create_index("ix_audit_events_run_id_action", "audit_events", ["run_id", "action"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_events_run_id_action", table_name="audit_events")
    op.drop_index("ix_audit_events_project_id_created_at", table_name="audit_events")
    op.drop_index(op.f("ix_audit_events_actor_id"), table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_stored_files_status_created_at", table_name="stored_files")
    op.drop_index(op.f("ix_stored_files_uploaded_by"), table_name="stored_files")
    op.drop_index(op.f("ix_stored_files_project_id"), table_name="stored_files")
    op.drop_table("stored_files")
