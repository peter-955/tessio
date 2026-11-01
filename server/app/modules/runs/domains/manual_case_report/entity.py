from app.modules.runs.domains.manual_step_report.entity import ManualStepReport
from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import Entity


class ManualCaseReport(Entity):
    status: ResultStatus | None
    duration_ms: int | None
    steps: list[ManualStepReport]
