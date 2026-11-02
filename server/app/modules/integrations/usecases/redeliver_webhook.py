from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.integrations.domains.webhook.repository import WebhookRepository
from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.modules.integrations.domains.webhook_delivery.repository import WebhookDeliveryRepository
from app.modules.integrations.errors import WebhookDeliveryNotFoundError, WebhookNotFoundError
from app.modules.integrations.ports.webhook_delivery_requester import WebhookDeliveryRequester
from app.modules.integrations.typing.enums.webhook import WebhookDeliveryStatus
from app.modules.integrations.utils.webhook_event import build_webhook_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class RedeliverWebhookUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        webhook_repository: WebhookRepository,
        webhook_delivery_repository: WebhookDeliveryRepository,
        webhook_delivery_requester: WebhookDeliveryRequester,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._webhook_repository = webhook_repository
        self._webhook_delivery_repository = webhook_delivery_repository
        self._webhook_delivery_requester = webhook_delivery_requester
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, webhook_id: UUID, delivery_id: UUID) -> WebhookDelivery:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            webhook = await self._webhook_repository.find(access.project_id, webhook_id)
            if webhook is None:
                raise WebhookNotFoundError
            original = await self._webhook_delivery_repository.find(webhook.id, delivery_id)
            if original is None:
                raise WebhookDeliveryNotFoundError
            redelivery = WebhookDelivery(
                id=uuid7(),
                webhook_id=webhook.id,
                event=original.event,
                payload=original.payload,
                status=WebhookDeliveryStatus.PENDING,
                attempts=0,
                response_status=None,
                error=None,
                redelivery_of_id=original.id,
                last_attempt_at=None,
                delivered_at=None,
                created_at=datetime.now(UTC),
            )
            await self._webhook_delivery_repository.save(redelivery)
        await self._webhook_delivery_requester.request(redelivery.id)
        await self._live_event_publisher.publish(build_webhook_changed_event(webhook.project_id, webhook.id))
        return redelivery
