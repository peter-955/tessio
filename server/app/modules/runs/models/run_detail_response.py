from uuid import UUID

from pydantic import Field

from app.modules.runs.models.run_case_response import RunCaseResponse
from app.modules.runs.models.run_data_value_response import RunDataValueResponse
from app.modules.runs.models.run_report_response import RunReportResponse
from app.modules.runs.models.run_summary_response import RunSummaryResponse
from app.modules.runs.models.skipped_run_case_response import SkippedRunCaseResponse


class RunDetailResponse(RunSummaryResponse):
    environment_base_url: str
    summary: str | None
    report: RunReportResponse | None
    child_run_ids: list[UUID]
    cases: list[RunCaseResponse]
    data: list[RunDataValueResponse]
    skipped_cases: list[SkippedRunCaseResponse] = Field(default_factory=list)
