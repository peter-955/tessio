from datetime import datetime
from uuid import UUID

from app.modules.test_cases import TestCaseStatus
from app.shared.common import Entity


class FlakyCase(Entity):
    test_case_id: UUID
    code: str
    title: str
    status: TestCaseStatus
    story_jira_key: str
    flaky_score: int
    flaky_since: datetime | None
    disagreed_at: datetime | None
    quarantined_at: datetime | None
