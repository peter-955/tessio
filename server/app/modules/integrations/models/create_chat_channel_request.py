from app.modules.integrations.typing.enums import ChatChannelKind
from app.modules.integrations.typing.types import ChatChannelEvents, ChatChannelName, ChatWebhookUrl
from app.shared.common import WireModel


class CreateChatChannelRequest(WireModel):
    kind: ChatChannelKind
    name: ChatChannelName
    webhook_url: ChatWebhookUrl
    events: ChatChannelEvents
    is_active: bool = True
