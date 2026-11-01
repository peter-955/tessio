from uuid import UUID

from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import Entity


class ManualStepReport(Entity):
    order: int
    status: ResultStatus
    actual_result: str
    error: str | None
    evidence_file_id: UUID | None
