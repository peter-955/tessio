from uuid import UUID

from app.modules.runs.typing.enums import ResultStatus, SuspectedCause
from app.shared.common import WireModel


class FailedCaseReportResponse(WireModel):
    test_case_id: UUID
    code: str
    title: str
    status: ResultStatus
    step_order: int | None
    step_action: str | None
    actual_result: str | None
    error: str | None
    suspected_cause: SuspectedCause | None = None
    cause_reason: str | None = None
    story_jira_key: str | None = None
