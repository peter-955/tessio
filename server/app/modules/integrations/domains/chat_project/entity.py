from uuid import UUID

from app.shared.common import Entity


class ChatProject(Entity):
    id: UUID
    key: str
    name: str
