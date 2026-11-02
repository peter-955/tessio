from datetime import datetime
from uuid import UUID

from app.modules.projects.typing.enums import JiraPostResults
from app.shared.common import WireModel
from app.shared.permissions import Capability, ProjectRole


class ProjectResponse(WireModel):
    id: UUID
    key: str
    name: str
    description: str | None
    jira_project_key: str | None
    jira_board_id: int | None
    is_linked_to_jira: bool
    allowed_file_types: list[str]
    is_archived: bool
    archived_at: datetime | None
    created_at: datetime
    my_role: ProjectRole | None
    capabilities: list[Capability]
    default_environment_id: UUID | None = None
    require_separate_reviewer: bool
    jira_bug_issue_type: str
    jira_post_results: JiraPostResults
