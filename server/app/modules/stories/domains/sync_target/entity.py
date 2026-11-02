from uuid import UUID

from app.shared.common import Entity


class SyncTarget(Entity):
    project_id: UUID
    project_key: str
    jira_project_key: str | None
    jira_board_id: int | None
    is_archived: bool
