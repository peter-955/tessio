from uuid import UUID

from app.modules.stories import TestStatus
from app.shared.common import Entity


class TracedStory(Entity):
    id: UUID
    jira_key: str
    title: str
    test_status: TestStatus
