from datetime import datetime

from pydantic import Field

from app.modules.runs.models.criterion_impact_response import CriterionImpactResponse
from app.modules.runs.models.failed_case_report_response import FailedCaseReportResponse
from app.modules.runs.models.missing_screenshot_response import MissingScreenshotResponse
from app.modules.runs.models.run_counts_response import RunCountsResponse
from app.modules.runs.models.run_report_story_response import RunReportStoryResponse
from app.modules.runs.models.skipped_run_case_response import SkippedRunCaseResponse
from app.modules.runs.models.unmapped_test_response import UnmappedTestResponse
from app.shared.common import WireModel


class RunReportResponse(WireModel):
    counts: RunCountsResponse
    failed_cases: list[FailedCaseReportResponse]
    criterion_impacts: list[CriterionImpactResponse]
    missing_screenshots: list[MissingScreenshotResponse]
    summary: str | None
    built_at: datetime
    stories: list[RunReportStoryResponse] = Field(default_factory=list)
    skipped_cases: list[SkippedRunCaseResponse] = Field(default_factory=list)
    unmapped_tests: list[UnmappedTestResponse] = Field(default_factory=list)
    unmapped_test_count: int = 0
