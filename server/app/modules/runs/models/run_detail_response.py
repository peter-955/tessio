from uuid import UUID

from app.modules.runs.models.run_case_response import RunCaseResponse
from app.modules.runs.models.run_report_response import RunReportResponse
from app.modules.runs.models.run_summary_response import RunSummaryResponse


class RunDetailResponse(RunSummaryResponse):
    summary: str | None
    report: RunReportResponse | None
    child_run_ids: list[UUID]
    cases: list[RunCaseResponse]
