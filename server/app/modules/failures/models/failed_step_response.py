from uuid import UUID

from app.modules.runs import StepDiagnosisResponse
from app.shared.common import WireModel


class FailedStepResponse(WireModel):
    step_order: int
    actual_result: str
    error: str | None
    screenshot_file_id: UUID | None
    diagnosis: StepDiagnosisResponse | None
