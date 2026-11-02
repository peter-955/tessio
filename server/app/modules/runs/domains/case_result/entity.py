from datetime import datetime
from uuid import UUID

from app.modules.runs.typing.enums import ResultStatus, SuspectedCause
from app.shared.common import Entity


class CaseResult(Entity):
    id: UUID
    run_id: UUID
    test_case_id: UUID
    test_case_version_id: UUID
    status: ResultStatus
    duration_ms: int | None
    suspected_cause: SuspectedCause | None
    cause_reason: str | None
    recorded_by: UUID
    created_at: datetime
    iteration: int = 0
