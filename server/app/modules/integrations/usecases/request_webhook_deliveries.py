from datetime import UTC, datetime
from uuid import uuid7

from app.modules.integrations.domains.webhook.repository import WebhookRepository
from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.modules.integrations.domains.webhook_delivery.repository import WebhookDeliveryRepository
from app.modules.integrations.ports.webhook_delivery_requester import WebhookDeliveryRequester
from app.modules.integrations.typing.constants import INTEGRATION_EVENT_BY_LIVE_EVENT
from app.modules.integrations.typing.enums.webhook import WebhookDeliveryStatus
from app.modules.integrations.utils.webhook_event import build_webhook_changed_event
from app.modules.integrations.utils.webhook_payload import build_webhook_payload
from app.modules.projects.domains.project.repository import ProjectRepository
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventHandler, LiveEventPublisher


class RequestWebhookDeliveriesUseCase(LiveEventHandler):
    def __init__(
        self,
        transaction: Transaction,
        project_repository: ProjectRepository,
        webhook_repository: WebhookRepository,
        webhook_delivery_repository: WebhookDeliveryRepository,
        webhook_delivery_requester: WebhookDeliveryRequester,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_repository = project_repository
        self._webhook_repository = webhook_repository
        self._webhook_delivery_repository = webhook_delivery_repository
        self._webhook_delivery_requester = webhook_delivery_requester
        self._live_event_publisher = live_event_publisher

    async def handle(self, event: LiveEvent) -> None:
        integration_event = INTEGRATION_EVENT_BY_LIVE_EVENT.get(event.type)
        if integration_event is None or event.project_id is None:
            return
        now = datetime.now(UTC)
        async with self._transaction.begin():
            webhooks = await self._webhook_repository.list_active_for_event(event.project_id, integration_event)
            if not webhooks:
                return
            project = await self._project_repository.find_by_id(event.project_id)
            if project is None:
                return
            payload = build_webhook_payload(uuid7(), integration_event, project, event.ids, now)
            deliveries = [
                WebhookDelivery(
                    id=uuid7(),
                    webhook_id=webhook.id,
                    event=integration_event,
                    payload=payload,
                    status=WebhookDeliveryStatus.PENDING,
                    attempts=0,
                    response_status=None,
                    error=None,
                    redelivery_of_id=None,
                    last_attempt_at=None,
                    delivered_at=None,
                    created_at=now,
                )
                for webhook in webhooks
            ]
            for delivery in deliveries:
                await self._webhook_delivery_repository.save(delivery)
        for delivery in deliveries:
            await self._webhook_delivery_requester.request(delivery.id)
            await self._live_event_publisher.publish(build_webhook_changed_event(event.project_id, delivery.webhook_id))
