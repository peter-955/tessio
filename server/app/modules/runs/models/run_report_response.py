from datetime import datetime

from app.modules.runs.models.criterion_impact_response import CriterionImpactResponse
from app.modules.runs.models.failed_case_report_response import FailedCaseReportResponse
from app.modules.runs.models.missing_screenshot_response import MissingScreenshotResponse
from app.modules.runs.models.run_counts_response import RunCountsResponse
from app.shared.common import WireModel


class RunReportResponse(WireModel):
    counts: RunCountsResponse
    failed_cases: list[FailedCaseReportResponse]
    criterion_impacts: list[CriterionImpactResponse]
    missing_screenshots: list[MissingScreenshotResponse]
    summary: str | None
    built_at: datetime
