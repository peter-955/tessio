from uuid import UUID

from app.modules.runs.typing.enums import RunStatus
from app.shared.common import Entity


class RunFilter(Entity):
    story_id: UUID | None
    status: RunStatus | None
    limit: int
