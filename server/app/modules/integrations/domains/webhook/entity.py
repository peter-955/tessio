from datetime import datetime
from uuid import UUID

from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.shared.common import Entity


class Webhook(Entity):
    id: UUID
    project_id: UUID
    url: str
    description: str | None
    secret_encrypted: bytes
    events: list[IntegrationEvent]
    is_active: bool
    created_by: UUID
    created_at: datetime
