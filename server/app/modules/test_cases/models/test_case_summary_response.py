from datetime import datetime
from uuid import UUID

from app.modules.test_cases.typing.enums import TestCasePriority, TestCaseStatus
from app.shared.common import WireModel


class TestCaseSummaryResponse(WireModel):
    id: UUID
    code: str
    story_id: UUID
    story_key: str
    title: str
    priority: TestCasePriority
    status: TestCaseStatus
    current_version_id: UUID
    current_version_number: int
    step_count: int
    criterion_ids: list[UUID]
    needs_review: bool
    needs_review_at: datetime | None
    last_saved_at: datetime
