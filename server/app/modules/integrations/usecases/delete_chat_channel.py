from uuid import UUID

from app.modules.integrations.domains.chat_channel.repository import ChatChannelRepository
from app.modules.integrations.errors import ChatChannelNotFoundError
from app.modules.integrations.utils.chat_channel_event import build_chat_channel_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class DeleteChatChannelUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        chat_channel_repository: ChatChannelRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._chat_channel_repository = chat_channel_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, chat_channel_id: UUID) -> None:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            chat_channel = await self._chat_channel_repository.find_by_id(access.project_id, chat_channel_id)
            if chat_channel is None:
                raise ChatChannelNotFoundError
            await self._chat_channel_repository.delete(chat_channel.id)
        await self._live_event_publisher.publish(
            build_chat_channel_changed_event(chat_channel.project_id, chat_channel.id)
        )
