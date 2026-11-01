from uuid import UUID

from app.shared.common import Entity


class ContextEnvironment(Entity):
    id: UUID
    name: str
    base_url: str
    health_check_url: str | None
    is_default: bool
