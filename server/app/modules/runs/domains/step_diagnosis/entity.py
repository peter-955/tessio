from app.modules.runs.domains.failed_request.entity import FailedRequest
from app.shared.common import Entity


class StepDiagnosis(Entity):
    page_url: str | None
    console_errors: list[str]
    failed_requests: list[FailedRequest]
