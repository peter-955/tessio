from uuid import UUID

from app.shared.common import Entity


class ChatGapDetails(Entity):
    id: UUID
    story_jira_key: str
    story_title: str
    question: str
    severity: str
    assignee_name: str | None
    assignee_role: str | None
    raised_by_name: str
