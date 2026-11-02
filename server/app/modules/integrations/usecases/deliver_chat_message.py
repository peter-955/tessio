from collections.abc import Awaitable, Callable
from uuid import UUID

from app.modules.integrations.domains.chat_channel.repository import ChatChannelRepository
from app.modules.integrations.domains.chat_delivery_job.entity import ChatDeliveryJob
from app.modules.integrations.domains.chat_message.entity import ChatMessage
from app.modules.integrations.domains.chat_project.entity import ChatProject
from app.modules.integrations.errors import ChatWebhookRejectedError
from app.modules.integrations.ports.chat_event_reader import ChatEventReader
from app.modules.integrations.typing.enums import IntegrationEvent
from app.modules.integrations.usecases.chat_message_delivery import ChatMessageDelivery
from app.modules.integrations.utils.chat_job_ids import read_job_id
from app.modules.integrations.utils.chat_message import (
    build_failure_message,
    build_gap_message,
    build_plan_message,
    build_run_message,
    build_story_message,
)
from app.shared.common import Transaction
from app.shared.logging import get_logger

log = get_logger(__name__)


class DeliverChatMessageUseCase:
    def __init__(
        self,
        transaction: Transaction,
        chat_channel_repository: ChatChannelRepository,
        chat_event_reader: ChatEventReader,
        chat_message_delivery: ChatMessageDelivery,
        client_url: str,
    ) -> None:
        self._transaction = transaction
        self._chat_channel_repository = chat_channel_repository
        self._chat_event_reader = chat_event_reader
        self._chat_message_delivery = chat_message_delivery
        self._client_url = client_url

    async def execute(self, job: ChatDeliveryJob) -> bool:
        log_extra = {"chat_channel_id": str(job.chat_channel_id), "event": job.event.value}
        async with self._transaction.begin():
            chat_channel = await self._chat_channel_repository.find_any(job.chat_channel_id)
            is_deliverable = (
                chat_channel is not None
                and chat_channel.project_id == job.project_id
                and chat_channel.is_subscribed_to(job.event)
            )
            project = await self._chat_event_reader.find_project(job.project_id) if is_deliverable else None
            message = None if project is None else await self._compose(job, project)
        if chat_channel is None or message is None:
            log.info("integrations.chat_delivery_skipped", extra=log_extra)
            return False
        try:
            await self._chat_message_delivery.deliver(chat_channel, message)
        except ChatWebhookRejectedError as error:
            log.warning(
                "integrations.chat_delivery_failed",
                extra={**log_extra, "reason": error.reason, "is_retryable": error.is_retryable},
            )
            if error.is_retryable:
                raise
            return False
        return True

    async def _compose(self, job: ChatDeliveryJob, project: ChatProject) -> ChatMessage | None:
        match job.event:
            case IntegrationEvent.RUN_STARTED | IntegrationEvent.RUN_FINISHED:
                run = await self._find(job, "runId", project, self._chat_event_reader.find_run)
                return None if run is None else build_run_message(job.event, run, project, self._client_url)
            case IntegrationEvent.FAILURE_OPENED | IntegrationEvent.FAILURE_STATUS_CHANGED:
                failure = await self._find(job, "failureId", project, self._chat_event_reader.find_failure)
                return None if failure is None else build_failure_message(job.event, failure, project, self._client_url)
            case IntegrationEvent.GAP_RAISED:
                gap = await self._find(job, "gapId", project, self._chat_event_reader.find_gap)
                return None if gap is None else build_gap_message(gap, project, self._client_url)
            case IntegrationEvent.STORY_SIGNED_OFF:
                story = await self._find(job, "storyId", project, self._chat_event_reader.find_story)
                return None if story is None else build_story_message(story, project, self._client_url)
            case IntegrationEvent.PLAN_SIGNED_OFF:
                plan = await self._find(job, "planId", project, self._chat_event_reader.find_plan)
                return None if plan is None else build_plan_message(plan, project, self._client_url)

    @staticmethod
    async def _find[Details](
        job: ChatDeliveryJob,
        key: str,
        project: ChatProject,
        find: Callable[[UUID, UUID], Awaitable[Details | None]],
    ) -> Details | None:
        target_id = read_job_id(job, key)
        return None if target_id is None else await find(project.id, target_id)
