from uuid import UUID

from app.modules.integrations.domains.chat_channel.entity import ChatChannel
from app.modules.integrations.domains.chat_channel.repository import ChatChannelRepository
from app.modules.integrations.errors import ChatChannelNotFoundError, ChatDeliveryFailedError, ChatWebhookRejectedError
from app.modules.integrations.ports.chat_event_reader import ChatEventReader
from app.modules.integrations.usecases.chat_message_delivery import ChatMessageDelivery
from app.modules.integrations.utils.chat_message import build_test_message
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class SendChatChannelTestUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        chat_channel_repository: ChatChannelRepository,
        chat_event_reader: ChatEventReader,
        chat_message_delivery: ChatMessageDelivery,
        client_url: str,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._chat_channel_repository = chat_channel_repository
        self._chat_event_reader = chat_event_reader
        self._chat_message_delivery = chat_message_delivery
        self._client_url = client_url

    async def execute(self, actor: Actor, project_key: str, chat_channel_id: UUID) -> ChatChannel:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            chat_channel = await self._chat_channel_repository.find_by_id(access.project_id, chat_channel_id)
            project = await self._chat_event_reader.find_project(access.project_id)
            if chat_channel is None or project is None:
                raise ChatChannelNotFoundError
        try:
            return await self._chat_message_delivery.deliver(
                chat_channel, build_test_message(chat_channel, project, self._client_url)
            )
        except ChatWebhookRejectedError as error:
            raise ChatDeliveryFailedError(error.reason) from None
