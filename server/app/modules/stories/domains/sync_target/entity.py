from uuid import UUID

from app.shared.common import Entity


class SyncTarget(Entity):
    project_id: UUID
    project_key: str
    jira_project_key: str
    jira_board_id: int
    is_archived: bool
