from datetime import datetime
from uuid import UUID

from app.modules.stories.typing.enums import SprintState
from app.shared.common import Entity


class Sprint(Entity):
    id: UUID
    project_id: UUID
    jira_sprint_id: int
    name: str
    state: SprintState
    start_at: datetime | None
    end_at: datetime | None
    complete_at: datetime | None
    synced_at: datetime
    created_at: datetime
