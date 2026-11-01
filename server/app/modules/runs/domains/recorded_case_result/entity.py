from datetime import datetime
from uuid import UUID

from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import Entity


class RecordedCaseResult(Entity):
    project_id: UUID
    story_id: UUID
    run_id: UUID
    case_result_id: UUID
    test_case_id: UUID
    status: ResultStatus
    recorded_by: UUID
    recorded_at: datetime
