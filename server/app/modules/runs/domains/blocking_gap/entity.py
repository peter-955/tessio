from uuid import UUID

from app.shared.common import Entity
from app.shared.permissions import ProjectRole


class BlockingGap(Entity):
    gap_id: UUID
    story_jira_key: str
    question: str
    assignee_name: str | None
    assignee_role: ProjectRole | None
