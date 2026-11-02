from app.modules.integrations.typing.types import ChatChannelEvents, ChatChannelName, ChatWebhookUrl
from app.shared.common import WireModel


class UpdateChatChannelRequest(WireModel):
    name: ChatChannelName | None = None
    webhook_url: ChatWebhookUrl | None = None
    events: ChatChannelEvents | None = None
    is_active: bool | None = None
