from datetime import datetime
from uuid import UUID

from app.modules.suites.models.suite_case_response import SuiteCaseResponse
from app.modules.suites.models.suite_run_reference_response import SuiteRunReferenceResponse
from app.shared.common import WireModel


class SuiteDetailResponse(WireModel):
    id: UUID
    name: str
    description: str | None
    archived_at: datetime | None
    created_by: UUID
    created_at: datetime
    case_count: int
    ready_case_count: int
    cases: list[SuiteCaseResponse]
    last_run: SuiteRunReferenceResponse | None
    running_run: SuiteRunReferenceResponse | None
