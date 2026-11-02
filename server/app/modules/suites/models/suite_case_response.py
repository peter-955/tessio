from uuid import UUID

from app.modules.test_cases import TestCasePriority, TestCaseStatus
from app.shared.common import WireModel


class SuiteCaseResponse(WireModel):
    test_case_id: UUID
    code: str
    title: str
    status: TestCaseStatus
    priority: TestCasePriority
    is_needing_review: bool
    is_runnable: bool
    story_id: UUID
    story_jira_key: str
    story_title: str
    position: int
