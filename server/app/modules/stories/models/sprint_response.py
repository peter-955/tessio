from datetime import datetime
from uuid import UUID

from app.modules.stories.typing.enums import SprintState
from app.shared.common import WireModel


class SprintResponse(WireModel):
    id: UUID
    jira_sprint_id: int
    name: str
    state: SprintState
    start_at: datetime | None
    end_at: datetime | None
    complete_at: datetime | None
    story_count: int
    synced_at: datetime
