from datetime import datetime
from uuid import UUID

from app.modules.test_cases.models.test_step_response import TestStepResponse
from app.modules.test_cases.typing.enums import TestCasePriority
from app.shared.common import WireModel


class TestCaseVersionResponse(WireModel):
    id: UUID
    number: int
    title: str
    priority: TestCasePriority
    business_value: str | None
    preconditions: str | None
    steps: list[TestStepResponse]
    criterion_ids: list[UUID]
    data_keys: list[str]
    file_version_ids: list[UUID]
    created_by: UUID
    created_at: datetime
    parameters: list[str]
    data_rows: list[dict[str, str]]
