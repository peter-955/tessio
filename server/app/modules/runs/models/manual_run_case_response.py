from uuid import UUID

from app.modules.runs.models.manual_run_step_response import ManualRunStepResponse
from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import WireModel


class ManualRunCaseResponse(WireModel):
    test_case_id: UUID
    test_case_version_id: UUID
    title: str
    steps: list[ManualRunStepResponse]
    result_status: ResultStatus | None
    parameters: list[str]
    data_rows: list[dict[str, str]]
