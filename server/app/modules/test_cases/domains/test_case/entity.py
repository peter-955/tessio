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
    flaky_score: int = 0
    flaky_since: datetime | None = None
    disagreed_at: datetime | None = None
    quarantined_at: datetime | None = None
    quarantined_by: UUID | None = None
    quarantine_reason: str | None = None

    @property
    def code(self) -> str:
        return f"{CASE_CODE_PREFIX}{self.number}"

    @property
    def is_needing_review(self) -> bool:
        return self.needs_review_at is not None

    @property
    def is_deprecated(self) -> bool:
        return self.status is TestCaseStatus.DEPRECATED

    @property
    def is_flaky(self) -> bool:
        return self.flaky_since is not None

    @property
    def is_disagreeing(self) -> bool:
        return self.disagreed_at is not None

    @property
    def is_quarantined(self) -> bool:
        return self.quarantined_at is not None
