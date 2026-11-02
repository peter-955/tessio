from app.modules.integrations.typing.enums import ChatChannelKind, IntegrationEvent
from app.shared.common import Entity


class NewChatChannel(Entity):
    kind: ChatChannelKind
    name: str
    webhook_url: str
    events: list[IntegrationEvent]
    is_active: bool
