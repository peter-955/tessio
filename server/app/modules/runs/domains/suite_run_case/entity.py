from uuid import UUID

from app.modules.test_cases import TestCaseStatus, TestCaseVersion
from app.shared.common import Entity


class SuiteRunCase(Entity):
    test_case_id: UUID
    code: str
    status: TestCaseStatus
    is_needing_review: bool
    story_id: UUID
    story_jira_key: str
    version: TestCaseVersion
