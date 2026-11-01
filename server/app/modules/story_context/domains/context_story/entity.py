from uuid import UUID

from app.modules.stories import TestStatus
from app.shared.common import Entity


class ContextStory(Entity):
    id: UUID
    jira_key: str
    title: str
    jira_status: str
    test_status: TestStatus
