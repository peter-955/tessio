from datetime import datetime
from uuid import UUID

from app.shared.common import WireModel
from app.shared.permissions import Capability, ProjectRole


class ProjectResponse(WireModel):
    id: UUID
    key: str
    name: str
    description: str | None
    jira_project_key: str
    jira_board_id: int
    allowed_file_types: list[str]
    is_archived: bool
    archived_at: datetime | None
    created_at: datetime
    my_role: ProjectRole | None
    capabilities: list[Capability]
    default_environment_id: UUID | None = None
