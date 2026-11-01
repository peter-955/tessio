from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class Project(Entity):
    id: UUID
    key: str
    name: str
    description: str | None
    jira_project_key: str
    jira_board_id: int
    allowed_file_types: list[str]
    archived_at: datetime | None
    created_at: datetime
    default_environment_id: UUID | None = None

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None
