from datetime import datetime
from uuid import UUID

from app.modules.suites.models.suite_run_reference_response import SuiteRunReferenceResponse
from app.shared.common import WireModel


class SuiteSummaryResponse(WireModel):
    id: UUID
    name: str
    description: str | None
    case_count: int
    ready_case_count: int
    archived_at: datetime | None
    created_at: datetime
    last_run: SuiteRunReferenceResponse | None
