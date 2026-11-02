from uuid import UUID

from app.shared.common import Entity


class RunSuite(Entity):
    id: UUID
    name: str
    is_archived: bool
