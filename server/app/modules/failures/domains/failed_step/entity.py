from uuid import UUID

from app.modules.runs import StepDiagnosis
from app.shared.common import Entity


class FailedStep(Entity):
    step_order: int
    actual_result: str
    error: str | None
    screenshot_file_id: UUID | None
    diagnosis: StepDiagnosis | None
