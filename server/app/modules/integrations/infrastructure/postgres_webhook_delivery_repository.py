from collections.abc import Collection
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import distinct_on

from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.modules.integrations.domains.webhook_delivery.repository import WebhookDeliveryRepository
from app.modules.integrations.infrastructure.webhook_delivery_table import WebhookDeliveryTable
from app.shared.postgres import Database


class PostgresWebhookDeliveryRepository(WebhookDeliveryRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self, webhook_id: UUID, delivery_id: UUID) -> WebhookDelivery | None:
        row = await self._database.get_current_session().scalar(
            select(WebhookDeliveryTable)
            .where(WebhookDeliveryTable.webhook_id == webhook_id, WebhookDeliveryTable.id == delivery_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else WebhookDelivery.model_validate(row)

    async def find_for_update(self, delivery_id: UUID) -> WebhookDelivery | None:
        row = await self._database.get_current_session().scalar(
            select(WebhookDeliveryTable)
            .where(WebhookDeliveryTable.id == delivery_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else WebhookDelivery.model_validate(row)

    async def list_for_webhook(self, webhook_id: UUID, limit: int) -> list[WebhookDelivery]:
        rows = await self._database.get_current_session().scalars(
            select(WebhookDeliveryTable)
            .where(WebhookDeliveryTable.webhook_id == webhook_id)
            .order_by(WebhookDeliveryTable.created_at.desc(), WebhookDeliveryTable.id.desc())
            .limit(limit)
            .execution_options(populate_existing=True)
        )
        return [WebhookDelivery.model_validate(row) for row in rows]

    async def map_latest(self, webhook_ids: Collection[UUID]) -> dict[UUID, WebhookDelivery]:
        if not webhook_ids:
            return {}
        rows = await self._database.get_current_session().scalars(
            select(WebhookDeliveryTable)
            .where(WebhookDeliveryTable.webhook_id.in_(sorted(webhook_ids)))
            .ext(distinct_on(WebhookDeliveryTable.webhook_id))
            .order_by(
                WebhookDeliveryTable.webhook_id,
                WebhookDeliveryTable.created_at.desc(),
                WebhookDeliveryTable.id.desc(),
            )
            .execution_options(populate_existing=True)
        )
        return {row.webhook_id: WebhookDelivery.model_validate(row) for row in rows}

    async def save(self, delivery: WebhookDelivery) -> None:
        await self._database.get_current_session().merge(WebhookDeliveryTable(**delivery.model_dump(mode="python")))

    async def delete_created_before(self, cutoff: datetime) -> int:
        result = await self._database.get_current_session().execute(
            delete(WebhookDeliveryTable)
            .where(WebhookDeliveryTable.created_at < cutoff)
            .returning(WebhookDeliveryTable.id)
        )
        return len(result.all())
