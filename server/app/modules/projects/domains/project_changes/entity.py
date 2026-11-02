from uuid import UUID

from app.modules.projects.typing.enums import JiraPostResults
from app.shared.common import Entity


class ProjectChanges(Entity):
    name: str | None = None
    description: str | None = None
    jira_board_id: int | None = None
    allowed_file_types: list[str] | None = None
    default_environment_id: UUID | None = None
    require_separate_reviewer: bool | None = None
    jira_bug_issue_type: str | None = None
    jira_post_results: JiraPostResults | None = None
    is_default_environment_cleared: bool = False
