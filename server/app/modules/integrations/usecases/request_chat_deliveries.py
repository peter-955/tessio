from app.modules.integrations.domains.chat_channel.repository import ChatChannelRepository
from app.modules.integrations.domains.chat_delivery_job.entity import ChatDeliveryJob
from app.modules.integrations.ports.chat_delivery_requester import ChatDeliveryRequester
from app.modules.integrations.typing.constants import INTEGRATION_EVENT_BY_LIVE_EVENT
from app.shared.common import Transaction
from app.shared.events import LiveEvent


class RequestChatDeliveriesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        chat_channel_repository: ChatChannelRepository,
        chat_delivery_requester: ChatDeliveryRequester,
    ) -> None:
        self._transaction = transaction
        self._chat_channel_repository = chat_channel_repository
        self._chat_delivery_requester = chat_delivery_requester

    async def execute(self, event: LiveEvent) -> list[ChatDeliveryJob]:
        integration_event = INTEGRATION_EVENT_BY_LIVE_EVENT.get(event.type)
        if integration_event is None or event.project_id is None:
            return []
        async with self._transaction.begin():
            chat_channels = await self._chat_channel_repository.list_subscribed(event.project_id, integration_event)
        jobs = [
            ChatDeliveryJob(
                chat_channel_id=chat_channel.id, project_id=event.project_id, event=integration_event, ids=event.ids
            )
            for chat_channel in chat_channels
        ]
        await self._chat_delivery_requester.request(jobs)
        return jobs
