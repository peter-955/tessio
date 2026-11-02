from uuid import UUID

from app.modules.test_cases import TestCaseVersion
from app.shared.common import Entity


class ImportCase(Entity):
    test_case_id: UUID
    number: int
    story_id: UUID
    version: TestCaseVersion
