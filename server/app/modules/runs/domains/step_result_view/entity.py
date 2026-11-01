from app.modules.files import StoredFileStatus
from app.modules.runs.domains.step_result.entity import StepResult
from app.modules.test_cases import TestStep
from app.shared.common import Entity


class StepResultView(Entity):
    step: TestStep
    result: StepResult | None
    screenshot_status: StoredFileStatus | None
