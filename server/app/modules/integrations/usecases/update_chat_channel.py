from uuid import UUID

from app.modules.integrations.domains.chat_channel.entity import ChatChannel
from app.modules.integrations.domains.chat_channel.repository import ChatChannelRepository
from app.modules.integrations.domains.chat_channel_change.entity import ChatChannelChange
from app.modules.integrations.errors import (
    ChatChannelNameAlreadyUsedError,
    ChatChannelNotFoundError,
    ChatWebhookUrlInvalidError,
)
from app.modules.integrations.utils.chat_channel_event import build_chat_channel_changed_event
from app.modules.integrations.utils.chat_channel_events import order_chat_events
from app.modules.integrations.utils.chat_channel_url import build_chat_webhook_url_hint, is_allowed_chat_webhook_url
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UpdateChatChannelUseCase:
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

    async def execute(
        self, actor: Actor, project_key: str, chat_channel_id: UUID, change: ChatChannelChange
    ) -> ChatChannel:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            chat_channel = await self._chat_channel_repository.find_by_id(access.project_id, chat_channel_id)
            if chat_channel is None:
                raise ChatChannelNotFoundError
            if change.webhook_url is not None and not is_allowed_chat_webhook_url(change.webhook_url):
                raise ChatWebhookUrlInvalidError
            if change.name is not None:
                same_name_channel = await self._chat_channel_repository.find_by_name(access.project_id, change.name)
                if same_name_channel is not None and same_name_channel.id != chat_channel.id:
                    raise ChatChannelNameAlreadyUsedError
            updated_chat_channel = self._apply(chat_channel, change)
            is_changing = updated_chat_channel != chat_channel
            if is_changing:
                await self._chat_channel_repository.save(updated_chat_channel)
        if is_changing:
            await self._live_event_publisher.publish(
                build_chat_channel_changed_event(chat_channel.project_id, chat_channel.id)
            )
        return updated_chat_channel

    def _apply(self, chat_channel: ChatChannel, change: ChatChannelChange) -> ChatChannel:
        updates: dict[str, object] = {}
        if change.name is not None:
            updates["name"] = change.name
        if change.events is not None:
            updates["events"] = order_chat_events(change.events)
        if change.is_active is not None:
            updates["is_active"] = change.is_active
        if change.webhook_url is not None:
            updates["webhook_url_encrypted"] = self._secret_cipher.encrypt(change.webhook_url.encode())
            updates["webhook_url_hint"] = build_chat_webhook_url_hint(change.webhook_url)
            updates["last_delivery_status"] = None
            updates["last_delivery_at"] = None
            updates["last_delivery_error"] = None
        return chat_channel.model_copy(update=updates)
