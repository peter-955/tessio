from uuid import UUID

from app.modules.test_cases import TestCaseStatus, TestCaseVersion
from app.shared.common import Entity


class StoryCase(Entity):
    test_case_id: UUID
    code: str
    status: TestCaseStatus
    version: TestCaseVersion
