from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.shared.common import Entity


class WebhookChanges(Entity):
    url: str | None = None
    description: str | None = None
    is_clearing_description: bool = False
    events: list[IntegrationEvent] | None = None
    is_active: bool | None = None
    is_rotating_secret: bool = False
