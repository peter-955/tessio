from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0028"
down_revision: str | None = "0027"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOTIFICATION_PREFERENCE_KINDS = (
    "gap_assigned",
    "failure_assigned",
    "run_finished",
    "suite_run_finished",
    "report_ready",
)
NOTIFICATION_CHANNELS = ("in_app", "email")
CHAT_CHANNEL_KINDS = ("slack", "teams")
CHAT_DELIVERY_STATUSES = ("delivered", "failed")
INTEGRATION_EVENTS = (
    "run.started",
    "run.finished",
    "failure.opened",
    "failure.status_changed",
    "gap.raised",
    "story.signed_off",
    "plan.signed_off",
)
CHAT_CHANNEL_EVENTS_CHECK = "project_chat_channel_events"


def build_text_enum(values: Sequence[str], name: str) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, create_constraint=True, length=40)


def build_events_check(values: Sequence[str]) -> str:
    quoted_values = ", ".join(f"'{value}'" for value in values)
    return f"cardinality(events) > 0 AND events <@ ARRAY[{quoted_values}]::text[]"


def upgrade() -> None:
    op.create_table(
        "notification_preferences",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "kind", build_text_enum(NOTIFICATION_PREFERENCE_KINDS, "notification_preference_kind"), nullable=False
        ),
        sa.Column("channel", build_text_enum(NOTIFICATION_CHANNELS, "notification_channel"), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id", "kind", "channel"),
    )
    op.create_table(
        "project_chat_channels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("kind", build_text_enum(CHAT_CHANNEL_KINDS, "chat_channel_kind"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("webhook_url_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("webhook_url_hint", sa.Text(), nullable=False),
        sa.Column("events", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "last_delivery_status",
            build_text_enum(CHAT_DELIVERY_STATUSES, "chat_delivery_status"),
            nullable=True,
        ),
        sa.Column("last_delivery_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_delivery_error", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(build_events_check(INTEGRATION_EVENTS), name=CHAT_CHANNEL_EVENTS_CHECK),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name"),
    )
    op.create_index(op.f("ix_project_chat_channels_project_id"), "project_chat_channels", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_project_chat_channels_project_id"), table_name="project_chat_channels")
    op.drop_table("project_chat_channels")
    op.drop_table("notification_preferences")
