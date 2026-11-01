from uuid import UUID

from app.modules.stories.typing.enums import TestStatus
from app.shared.common import Entity


class StoryFilter(Entity):
    sprint_id: UUID | None = None
    test_status: TestStatus | None = None
    query: str | None = None
