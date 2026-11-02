from datetime import datetime
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.modules.integrations.typing.enums.webhook import WebhookDeliveryStatus
from app.shared.postgres import TableBase, build_text_enum


class WebhookDeliveryTable(TableBase):
    __tablename__ = "webhook_deliveries"
    __table_args__ = (Index("ix_webhook_deliveries_webhook_id_created_at", "webhook_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    webhook_id: Mapped[UUID] = mapped_column(ForeignKey("webhooks.id", ondelete="CASCADE"))
    event: Mapped[IntegrationEvent] = mapped_column(build_text_enum(IntegrationEvent, "webhook_event"))
    payload: Mapped[JsonValue] = mapped_column(JSONB, nullable=False)
    status: Mapped[WebhookDeliveryStatus] = mapped_column(
        build_text_enum(WebhookDeliveryStatus, "webhook_delivery_status")
    )
    attempts: Mapped[int]
    response_status: Mapped[int | None]
    error: Mapped[str | None] = mapped_column(Text)
    redelivery_of_id: Mapped[UUID | None] = mapped_column(ForeignKey("webhook_deliveries.id", ondelete="SET NULL"))
    last_attempt_at: Mapped[datetime | None]
    delivered_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(index=True)
