from datetime import UTC, datetime

from app.modules.integrations.domains.webhook_delivery.repository import WebhookDeliveryRepository
from app.modules.integrations.typing.constants.webhook import WEBHOOK_DELIVERY_RETENTION
from app.shared.common import Transaction


class DeleteOldWebhookDeliveriesUseCase:
    def __init__(self, transaction: Transaction, webhook_delivery_repository: WebhookDeliveryRepository) -> None:
        self._transaction = transaction
        self._webhook_delivery_repository = webhook_delivery_repository

    async def execute(self) -> int:
        cutoff = datetime.now(UTC) - WEBHOOK_DELIVERY_RETENTION
        async with self._transaction.begin():
            return await self._webhook_delivery_repository.delete_created_before(cutoff)
