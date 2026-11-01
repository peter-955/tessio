from uuid import UUID

from app.modules.test_cases.typing.enums import TestCasePriority, TestCaseStatus
from app.shared.common import Entity


class TestCaseFilter(Entity):
    story_key: str | None = None
    status: TestCaseStatus | None = None
    priority: TestCasePriority | None = None
    criterion_id: UUID | None = None
    is_needing_review: bool | None = None
    query: str | None = None
