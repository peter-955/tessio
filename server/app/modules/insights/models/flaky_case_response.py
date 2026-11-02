from datetime import datetime
from uuid import UUID

from app.modules.test_cases import TestCaseStatus
from app.shared.common import WireModel


class FlakyCaseResponse(WireModel):
    test_case_id: UUID
    code: str
    title: str
    status: TestCaseStatus
    story_jira_key: str
    flaky_score: int
    is_flaky: bool
    flaky_since: datetime | None
    is_disagreeing: bool
    disagreed_at: datetime | None
    is_quarantined: bool
    quarantined_at: datetime | None
