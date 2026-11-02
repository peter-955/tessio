from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, LargeBinary, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.integrations.typing.enums import ChatChannelKind, ChatDeliveryStatus, IntegrationEvent
from app.shared.postgres import TableBase, build_text_enum

CHAT_CHANNEL_EVENT_VALUES = ", ".join(f"'{event.value}'" for event in IntegrationEvent)


class ProjectChatChannelTable(TableBase):
    __tablename__ = "project_chat_channels"
    __table_args__ = (
        UniqueConstraint("project_id", "name"),
        CheckConstraint(
            f"cardinality(events) > 0 AND events <@ ARRAY[{CHAT_CHANNEL_EVENT_VALUES}]::text[]",
            name="project_chat_channel_events",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    kind: Mapped[ChatChannelKind] = mapped_column(build_text_enum(ChatChannelKind, "chat_channel_kind"))
    name: Mapped[str] = mapped_column(Text)
    webhook_url_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    webhook_url_hint: Mapped[str] = mapped_column(Text)
    events: Mapped[list[str]] = mapped_column(ARRAY(Text))
    is_active: Mapped[bool]
    last_delivery_status: Mapped[ChatDeliveryStatus | None] = mapped_column(
        build_text_enum(ChatDeliveryStatus, "chat_delivery_status")
    )
    last_delivery_at: Mapped[datetime | None]
    last_delivery_error: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
