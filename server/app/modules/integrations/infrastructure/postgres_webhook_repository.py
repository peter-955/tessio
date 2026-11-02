from uuid import UUID

from sqlalchemy import delete, func, select

from app.modules.integrations.domains.webhook.entity import Webhook
from app.modules.integrations.domains.webhook.repository import WebhookRepository
from app.modules.integrations.infrastructure.webhook_table import WebhookTable
from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.shared.postgres import Database


class PostgresWebhookRepository(WebhookRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self, project_id: UUID, webhook_id: UUID) -> Webhook | None:
        row = await self._database.get_current_session().scalar(
            select(WebhookTable)
            .where(WebhookTable.project_id == project_id, WebhookTable.id == webhook_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else Webhook.model_validate(row)

    async def find_by_id(self, webhook_id: UUID) -> Webhook | None:
        row = await self._database.get_current_session().scalar(
            select(WebhookTable).where(WebhookTable.id == webhook_id).execution_options(populate_existing=True)
        )
        return None if row is None else Webhook.model_validate(row)

    async def list_for_project(self, project_id: UUID) -> list[Webhook]:
        rows = await self._database.get_current_session().scalars(
            select(WebhookTable)
            .where(WebhookTable.project_id == project_id)
            .order_by(WebhookTable.created_at, WebhookTable.id)
            .execution_options(populate_existing=True)
        )
        return [Webhook.model_validate(row) for row in rows]

    async def list_active_for_event(self, project_id: UUID, event: IntegrationEvent) -> list[Webhook]:
        rows = await self._database.get_current_session().scalars(
            select(WebhookTable)
            .where(
                WebhookTable.project_id == project_id,
                WebhookTable.is_active.is_(True),
                WebhookTable.events.contains([event.value]),
            )
            .order_by(WebhookTable.created_at, WebhookTable.id)
            .execution_options(populate_existing=True)
        )
        return [Webhook.model_validate(row) for row in rows]

    async def count_for_project(self, project_id: UUID) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count()).select_from(WebhookTable).where(WebhookTable.project_id == project_id)
        )
        return int(count or 0)

    async def save(self, webhook: Webhook) -> None:
        await self._database.get_current_session().merge(WebhookTable(**webhook.model_dump(mode="python")))

    async def delete(self, webhook_id: UUID) -> None:
        await self._database.get_current_session().execute(delete(WebhookTable).where(WebhookTable.id == webhook_id))
