from datetime import datetime
from uuid import UUID

from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import Entity


class StepResult(Entity):
    id: UUID
    case_result_id: UUID
    step_order: int
    status: ResultStatus
    actual_result: str | None
    error: str | None
    screenshot_file_id: UUID | None
    evidence_file_id: UUID | None
    created_at: datetime
