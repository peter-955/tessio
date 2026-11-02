from datetime import UTC, datetime

from app.modules.integrations.domains.chat_channel.entity import ChatChannel
from app.modules.integrations.domains.chat_channel.repository import ChatChannelRepository
from app.modules.integrations.domains.chat_message.entity import ChatMessage
from app.modules.integrations.errors import ChatWebhookRejectedError
from app.modules.integrations.ports.chat_webhook_sender import ChatWebhookSender
from app.modules.integrations.typing.constants import MAX_CHAT_DELIVERY_ERROR_LENGTH
from app.modules.integrations.typing.enums import ChatDeliveryStatus
from app.modules.integrations.utils.chat_channel_event import build_chat_channel_changed_event
from app.modules.integrations.utils.chat_payload import build_chat_payload
from app.modules.integrations.utils.chat_text import shorten_chat_text
from app.shared.common import Transaction
from app.shared.crypto import InvalidCipherTextError, SecretCipher
from app.shared.events import LiveEventPublisher

UNREADABLE_URL_REASON = "The saved webhook URL could not be read. Save the URL again."


class ChatMessageDelivery:
    def __init__(
        self,
        transaction: Transaction,
        chat_channel_repository: ChatChannelRepository,
        secret_cipher: SecretCipher,
        chat_webhook_sender: ChatWebhookSender,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._chat_channel_repository = chat_channel_repository
        self._secret_cipher = secret_cipher
        self._chat_webhook_sender = chat_webhook_sender
        self._live_event_publisher = live_event_publisher

    async def deliver(self, chat_channel: ChatChannel, message: ChatMessage) -> ChatChannel:
        try:
            webhook_url = self._secret_cipher.decrypt(chat_channel.webhook_url_encrypted).decode()
        except InvalidCipherTextError, UnicodeDecodeError:
            await self._record(chat_channel, ChatDeliveryStatus.FAILED, UNREADABLE_URL_REASON)
            raise ChatWebhookRejectedError(UNREADABLE_URL_REASON, is_retryable=False) from None
        try:
            await self._chat_webhook_sender.send(webhook_url, build_chat_payload(chat_channel.kind, message))
        except ChatWebhookRejectedError as error:
            await self._record(
                chat_channel, ChatDeliveryStatus.FAILED, shorten_chat_text(error.reason, MAX_CHAT_DELIVERY_ERROR_LENGTH)
            )
            raise
        return await self._record(chat_channel, ChatDeliveryStatus.DELIVERED, None)

    async def _record(self, chat_channel: ChatChannel, status: ChatDeliveryStatus, error: str | None) -> ChatChannel:
        delivered_at = datetime.now(UTC)
        async with self._transaction.begin():
            await self._chat_channel_repository.record_delivery(chat_channel.id, status, delivered_at, error)
        await self._live_event_publisher.publish(
            build_chat_channel_changed_event(chat_channel.project_id, chat_channel.id)
        )
        return chat_channel.model_copy(
            update={"last_delivery_status": status, "last_delivery_at": delivered_at, "last_delivery_error": error}
        )
