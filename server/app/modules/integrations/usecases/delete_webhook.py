from uuid import UUID

from app.modules.integrations.domains.webhook.repository import WebhookRepository
from app.modules.integrations.errors import WebhookNotFoundError
from app.modules.integrations.utils.webhook_event import build_webhook_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class DeleteWebhookUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        webhook_repository: WebhookRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._webhook_repository = webhook_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, webhook_id: UUID) -> None:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            webhook = await self._webhook_repository.find(access.project_id, webhook_id)
            if webhook is None:
                raise WebhookNotFoundError
            await self._webhook_repository.delete(webhook.id)
        await self._live_event_publisher.publish(build_webhook_changed_event(webhook.project_id, webhook.id))
