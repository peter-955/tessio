from uuid import UUID

from app.modules.files import StoredFileStatus
from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import WireModel


class StepResultResponse(WireModel):
    order: int
    action: str
    expected: str | None
    status: ResultStatus | None
    actual_result: str | None
    error: str | None
    screenshot_file_id: UUID | None
    screenshot_status: StoredFileStatus | None
    evidence_file_id: UUID | None
