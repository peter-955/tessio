from app.modules.integrations.domains.chat_channel.entity import ChatChannel
from app.modules.integrations.models.chat_channel_response import ChatChannelResponse


def build_chat_channel_response(chat_channel: ChatChannel) -> ChatChannelResponse:
    return ChatChannelResponse(
        id=chat_channel.id,
        kind=chat_channel.kind,
        name=chat_channel.name,
        webhook_url_masked=chat_channel.webhook_url_hint,
        events=chat_channel.events,
        is_active=chat_channel.is_active,
        last_delivery_status=chat_channel.last_delivery_status,
        last_delivery_at=chat_channel.last_delivery_at,
        last_delivery_error=chat_channel.last_delivery_error,
        created_at=chat_channel.created_at,
    )
