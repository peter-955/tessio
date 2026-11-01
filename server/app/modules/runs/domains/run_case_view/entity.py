from uuid import UUID

from app.modules.test_cases import TestCaseVersion
from app.shared.common import Entity


class RunCaseView(Entity):
    test_case_id: UUID
    code: str
    position: int
    version: TestCaseVersion
