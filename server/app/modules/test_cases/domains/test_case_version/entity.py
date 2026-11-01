from datetime import datetime
from uuid import UUID

from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.typing.enums import TestCasePriority
from app.shared.common import Entity


class TestCaseVersion(Entity):
    id: UUID
    test_case_id: UUID
    number: int
    title: str
    priority: TestCasePriority
    business_value: str | None
    preconditions: str | None
    steps: list[TestStep]
    criterion_ids: list[UUID]
    data_keys: list[str]
    file_version_ids: list[UUID]
    created_by: UUID
    created_at: datetime
