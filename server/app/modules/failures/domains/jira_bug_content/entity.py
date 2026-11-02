from uuid import UUID

from app.modules.jira import JiraDocumentBlock
from app.shared.common import Entity


class JiraBugContent(Entity):
    jira_project_key: str
    issue_type_name: str
    summary: str
    description: list[JiraDocumentBlock]
    linked_story_jira_key: str | None
    screenshot_file_id: UUID | None
