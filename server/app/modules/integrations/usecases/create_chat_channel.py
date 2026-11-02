from datetime import UTC, datetime
from uuid import uuid7

from app.modules.integrations.domains.chat_channel.entity import ChatChannel
from app.modules.integrations.domains.chat_channel.repository import ChatChannelRepository
from app.modules.integrations.domains.new_chat_channel.entity import NewChatChannel
from app.modules.integrations.errors import (
    ChatChannelLimitReachedError,
    ChatChannelNameAlreadyUsedError,
    ChatWebhookUrlInvalidError,
)
from app.modules.integrations.typing.constants import MAX_CHAT_CHANNELS_PER_PROJECT
from app.modules.integrations.utils.chat_channel_event import build_chat_channel_changed_event
from app.modules.integrations.utils.chat_channel_events import order_chat_events
from app.modules.integrations.utils.chat_channel_url import build_chat_webhook_url_hint, is_allowed_chat_webhook_url
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CreateChatChannelUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        chat_channel_repository: ChatChannelRepository,
        secret_cipher: SecretCipher,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._chat_channel_repository = chat_channel_repository
        self._secret_cipher = secret_cipher
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, new_chat_channel: NewChatChannel) -> ChatChannel:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            if not is_allowed_chat_webhook_url(new_chat_channel.webhook_url):
                raise ChatWebhookUrlInvalidError
            if (
                await self._chat_channel_repository.count_for_project(access.project_id)
                >= MAX_CHAT_CHANNELS_PER_PROJECT
            ):
                raise ChatChannelLimitReachedError(MAX_CHAT_CHANNELS_PER_PROJECT)
            if await self._chat_channel_repository.find_by_name(access.project_id, new_chat_channel.name) is not None:
                raise ChatChannelNameAlreadyUsedError
            chat_channel = ChatChannel(
                id=uuid7(),
                project_id=access.project_id,
                kind=new_chat_channel.kind,
                name=new_chat_channel.name,
                webhook_url_encrypted=self._secret_cipher.encrypt(new_chat_channel.webhook_url.encode()),
                webhook_url_hint=build_chat_webhook_url_hint(new_chat_channel.webhook_url),
                events=order_chat_events(new_chat_channel.events),
                is_active=new_chat_channel.is_active,
                last_delivery_status=None,
                last_delivery_at=None,
                last_delivery_error=None,
                created_by=actor.user_id,
                created_at=datetime.now(UTC),
            )
            await self._chat_channel_repository.save(chat_channel)
        await self._live_event_publisher.publish(
            build_chat_channel_changed_event(chat_channel.project_id, chat_channel.id)
        )
        return chat_channel
