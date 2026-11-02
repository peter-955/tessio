from uuid import UUID

from pydantic import JsonValue

from app.modules.integrations.typing.constants.webhook import WEBHOOK_DELIVERY_JOB_ID_KEY
from app.modules.integrations.usecases.deliver_webhook import DeliverWebhookUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class DeliverWebhookJobHandler(JobHandler):
    def __init__(self, use_case: DeliverWebhookUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        delivery_id_value = data.get(WEBHOOK_DELIVERY_JOB_ID_KEY)
        try:
            delivery_id = UUID(delivery_id_value) if isinstance(delivery_id_value, str) else None
        except ValueError:
            delivery_id = None
        if delivery_id is None:
            log.warning("integrations.webhook_invalid_job_data", extra={"delivery_id": str(delivery_id_value)})
            return
        await self._use_case.execute(delivery_id)
