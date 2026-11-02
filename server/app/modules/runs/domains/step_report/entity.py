from app.modules.runs.domains.failed_request.entity import FailedRequest
from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import Entity


class StepReport(Entity):
    order: int
    status: ResultStatus
    actual_result: str
    error: str | None
    screenshot_path: str | None
    page_url: str | None
    console_errors: list[str]
    failed_requests: list[FailedRequest]
