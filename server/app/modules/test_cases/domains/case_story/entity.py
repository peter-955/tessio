from uuid import UUID

from app.shared.common import Entity


class CaseStory(Entity):
    id: UUID
    jira_key: str
    title: str
