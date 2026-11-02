from app.modules.integrations.typing.enums import IntegrationEvent
from app.shared.common import Entity


class ChatChannelChange(Entity):
    name: str | None
    webhook_url: str | None
    events: list[IntegrationEvent] | None
    is_active: bool | None
