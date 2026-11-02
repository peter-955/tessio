from datetime import UTC, datetime
from uuid import UUID

from app.modules.integrations.domains.webhook.entity import Webhook
from app.modules.integrations.domains.webhook.repository import WebhookRepository
from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.modules.integrations.domains.webhook_delivery.repository import WebhookDeliveryRepository
from app.modules.integrations.domains.webhook_send_result.entity import WebhookSendResult
from app.modules.integrations.errors import WebhookAttemptFailedError
from app.modules.integrations.ports.webhook_sender import WebhookSender
from app.modules.integrations.typing.enums.webhook import WebhookDeliveryStatus
from app.modules.integrations.utils.webhook_event import build_webhook_changed_event
from app.modules.integrations.utils.webhook_payload import build_webhook_headers, serialize_webhook_payload
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.events import LiveEventPublisher
from app.shared.typing.constants import JOB_ATTEMPTS

WEBHOOK_TURNED_OFF_ERROR = "The webhook is turned off."


class DeliverWebhookUseCase:
    def __init__(
        self,
        transaction: Transaction,
        webhook_repository: WebhookRepository,
        webhook_delivery_repository: WebhookDeliveryRepository,
        webhook_sender: WebhookSender,
        secret_cipher: SecretCipher,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._webhook_repository = webhook_repository
        self._webhook_delivery_repository = webhook_delivery_repository
        self._webhook_sender = webhook_sender
        self._secret_cipher = secret_cipher
        self._live_event_publisher = live_event_publisher

    async def execute(self, delivery_id: UUID) -> WebhookDelivery | None:
        async with self._transaction.begin():
            delivery = await self._webhook_delivery_repository.find_for_update(delivery_id)
            if delivery is None or delivery.status is not WebhookDeliveryStatus.PENDING:
                return delivery
            webhook = await self._webhook_repository.find_by_id(delivery.webhook_id)
        if webhook is None:
            return None
        now = datetime.now(UTC)
        result = await self._send(webhook, delivery, now)
        attempts = delivery.attempts + 1
        recorded = delivery.model_copy(
            update={
                "attempts": attempts,
                "status": self._decide_status(webhook, result, attempts),
                "response_status": result.response_status,
                "error": result.error,
                "last_attempt_at": now,
                "delivered_at": now if result.is_success else None,
            }
        )
        async with self._transaction.begin():
            if await self._webhook_delivery_repository.find_for_update(delivery.id) is None:
                return None
            await self._webhook_delivery_repository.save(recorded)
        await self._live_event_publisher.publish(build_webhook_changed_event(webhook.project_id, webhook.id))
        if recorded.status is WebhookDeliveryStatus.PENDING:
            raise WebhookAttemptFailedError(result.error or "")
        return recorded

    async def _send(self, webhook: Webhook, delivery: WebhookDelivery, now: datetime) -> WebhookSendResult:
        if not webhook.is_active:
            return WebhookSendResult(is_success=False, response_status=None, error=WEBHOOK_TURNED_OFF_ERROR)
        secret = self._secret_cipher.decrypt(webhook.secret_encrypted).decode()
        body = serialize_webhook_payload(delivery.payload)
        headers = build_webhook_headers(delivery, secret, body, int(now.timestamp()))
        return await self._webhook_sender.send(webhook.url, body, headers)

    @staticmethod
    def _decide_status(webhook: Webhook, result: WebhookSendResult, attempts: int) -> WebhookDeliveryStatus:
        if result.is_success:
            return WebhookDeliveryStatus.SUCCEEDED
        if not webhook.is_active or attempts >= JOB_ATTEMPTS:
            return WebhookDeliveryStatus.FAILED
        return WebhookDeliveryStatus.PENDING
