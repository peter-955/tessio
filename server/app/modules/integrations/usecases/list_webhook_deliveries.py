from uuid import UUID

from app.modules.integrations.domains.webhook.repository import WebhookRepository
from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.modules.integrations.domains.webhook_delivery.repository import WebhookDeliveryRepository
from app.modules.integrations.errors import WebhookNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListWebhookDeliveriesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        webhook_repository: WebhookRepository,
        webhook_delivery_repository: WebhookDeliveryRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._webhook_repository = webhook_repository
        self._webhook_delivery_repository = webhook_delivery_repository

    async def execute(self, actor: Actor, project_key: str, webhook_id: UUID, limit: int) -> list[WebhookDelivery]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            webhook = await self._webhook_repository.find(access.project_id, webhook_id)
            if webhook is None:
                raise WebhookNotFoundError
            return await self._webhook_delivery_repository.list_for_webhook(webhook.id, limit)
