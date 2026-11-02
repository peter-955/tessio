from pydantic import JsonValue, ValidationError

from app.modules.integrations.domains.chat_delivery_job.entity import ChatDeliveryJob
from app.modules.integrations.usecases.deliver_chat_message import DeliverChatMessageUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class DeliverChatMessageJobHandler(JobHandler):
    def __init__(self, use_case: DeliverChatMessageUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        try:
            job = ChatDeliveryJob.model_validate(data)
        except ValidationError:
            log.warning("integrations.chat_invalid_job_data")
            return
        await self._use_case.execute(job)
