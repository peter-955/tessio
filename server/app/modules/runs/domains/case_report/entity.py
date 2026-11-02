from uuid import UUID

from app.modules.runs.domains.step_report.entity import StepReport
from app.modules.runs.typing.enums import ResultStatus, SuspectedCause
from app.shared.common import Entity


class CaseReport(Entity):
    run_id: UUID
    case_id: UUID
    status: ResultStatus
    duration_ms: int
    steps: list[StepReport]
    suspected_cause: SuspectedCause | None
    cause_reason: str | None
    iteration: int = 0
