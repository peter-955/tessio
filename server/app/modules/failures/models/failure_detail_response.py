from app.modules.failures.models.failed_step_response import FailedStepResponse
from app.modules.failures.models.failure_event_response import FailureEventResponse
from app.modules.failures.models.failure_response import FailureResponse
from app.modules.failures.models.failure_result_response import FailureResultResponse


class FailureDetailResponse(FailureResponse):
    failed_step: FailedStepResponse | None
    results: list[FailureResultResponse]
    events: list[FailureEventResponse]
