from uuid import UUID

from app.shared.common import Entity


class RunStory(Entity):
    id: UUID
    jira_key: str
    title: str
