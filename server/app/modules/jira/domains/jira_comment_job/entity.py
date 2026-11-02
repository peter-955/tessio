from uuid import UUID

from app.modules.jira.typing.enums import JiraCommentTrigger
from app.shared.common import Entity


class JiraCommentJob(Entity):
    trigger: JiraCommentTrigger
    project_id: UUID
    story_id: UUID
    run_id: UUID | None
