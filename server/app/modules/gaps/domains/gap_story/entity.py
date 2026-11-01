from uuid import UUID

from app.shared.common import Entity


class GapStory(Entity):
    id: UUID
    jira_key: str
    title: str
