from pydantic import JsonValue

from app.modules.integrations.usecases.delete_old_webhook_deliveries import DeleteOldWebhookDeliveriesUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class DeleteOldWebhookDeliveriesJobHandler(JobHandler):
    def __init__(self, use_case: DeleteOldWebhookDeliveriesUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        deleted_count = await self._use_case.execute()
        log.info("integrations.webhook_deliveries_deleted", extra={"count": deleted_count})
