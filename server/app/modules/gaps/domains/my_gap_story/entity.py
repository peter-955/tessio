from uuid import UUID

from app.shared.common import Entity


class MyGapStory(Entity):
    id: UUID
    jira_key: str
    title: str
    open_gap_count: int

    @property
    def is_ready(self) -> bool:
        return self.open_gap_count == 0
