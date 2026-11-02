from app.modules.runs.models.failed_request_response import FailedRequestResponse
from app.shared.common import WireModel


class StepDiagnosisResponse(WireModel):
    page_url: str | None
    console_errors: list[str]
    failed_requests: list[FailedRequestResponse]
