from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, LargeBinary, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.shared.postgres import TableBase

WEBHOOK_EVENT_VALUES = ", ".join(f"'{event.value}'" for event in IntegrationEvent)


class WebhookTable(TableBase):
    __tablename__ = "webhooks"
    __table_args__ = (
        CheckConstraint(
            f"cardinality(events) > 0 AND events <@ ARRAY[{WEBHOOK_EVENT_VALUES}]::text[]", name="webhook_events"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    url: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    secret_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    events: Mapped[list[str]] = mapped_column(ARRAY(Text))
    is_active: Mapped[bool]
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
