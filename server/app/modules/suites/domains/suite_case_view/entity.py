from uuid import UUID

from app.modules.test_cases import TestCasePriority, TestCaseStatus
from app.shared.common import Entity


class SuiteCaseView(Entity):
    test_case_id: UUID
    code: str
    title: str
    status: TestCaseStatus
    priority: TestCasePriority
    is_needing_review: bool
    story_id: UUID
    story_jira_key: str
    story_title: str
    position: int

    @property
    def is_runnable(self) -> bool:
        return self.status is TestCaseStatus.READY and not self.is_needing_review
