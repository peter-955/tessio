from pydantic import Field

from app.modules.runs.models.manual_step_result_input import ManualStepResultInput
from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import WireModel


class ManualCaseResultRequest(WireModel):
    status: ResultStatus | None = None
    duration_ms: int | None = Field(default=None, ge=0, le=86_400_000)
    steps: list[ManualStepResultInput] = Field(default_factory=list, max_length=200)
