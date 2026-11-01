from datetime import datetime
from uuid import UUID

from app.modules.test_cases.typing.constants import CASE_CODE_PREFIX
from app.modules.test_cases.typing.enums import TestCasePriority, TestCaseStatus
from app.shared.common import Entity


class TestCase(Entity):
    id: UUID
    project_id: UUID
    story_id: UUID
    number: int
    title: str
    priority: TestCasePriority
    status: TestCaseStatus
    current_version_id: UUID
    status_changed_at: datetime | None
    status_changed_by: UUID | None
    needs_review_at: datetime | None
    needs_review_criterion_ids: list[UUID]
    reviewed_at: datetime | None
    reviewed_by: UUID | None
    created_by: UUID
    created_at: datetime

    @property
    def code(self) -> str:
        return f"{CASE_CODE_PREFIX}{self.number}"

    @property
    def is_needing_review(self) -> bool:
        return self.needs_review_at is not None

    @property
    def is_deprecated(self) -> bool:
        return self.status is TestCaseStatus.DEPRECATED
