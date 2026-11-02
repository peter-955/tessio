from datetime import datetime
from uuid import UUID

from app.modules.projects.typing.constants import DEFAULT_JIRA_BUG_ISSUE_TYPE
from app.modules.projects.typing.enums import JiraPostResults
from app.shared.common import Entity


class Project(Entity):
    id: UUID
    key: str
    name: str
    description: str | None
    jira_project_key: str | None
    jira_board_id: int | None
    allowed_file_types: list[str]
    archived_at: datetime | None
    created_at: datetime
    default_environment_id: UUID | None = None
    require_separate_reviewer: bool = False
    jira_bug_issue_type: str = DEFAULT_JIRA_BUG_ISSUE_TYPE
    jira_post_results: JiraPostResults = JiraPostResults.OFF

    @property
    def is_linked_to_jira(self) -> bool:
        return self.jira_project_key is not None

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None
