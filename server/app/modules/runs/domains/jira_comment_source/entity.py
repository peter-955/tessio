from uuid import UUID

from app.modules.runs.domains.run_counts.entity import RunCounts
from app.modules.runs.typing.enums import RunStatus
from app.shared.common import Entity


class JiraCommentSource(Entity):
    project_key: str
    is_project_linked: bool
    story_jira_key: str
    story_title: str
    is_story_from_jira: bool
    run_id: UUID | None
    run_status: RunStatus | None
    environment_name: str | None
    counts: RunCounts | None
