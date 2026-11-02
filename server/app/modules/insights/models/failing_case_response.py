from datetime import datetime
from uuid import UUID

from app.modules.test_cases import TestCaseStatus
from app.shared.common import WireModel


class FailingCaseResponse(WireModel):
    test_case_id: UUID
    code: str
    title: str
    status: TestCaseStatus
    story_jira_key: str
    result_count: int
    failed_count: int
    blocked_count: int
    fail_rate: float
    last_failed_at: datetime
    is_flaky: bool
    is_quarantined: bool
