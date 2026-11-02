from datetime import datetime

from pydantic import Field

from app.modules.runs.domains.criterion_impact.entity import CriterionImpact
from app.modules.runs.domains.failed_case_report.entity import FailedCaseReport
from app.modules.runs.domains.missing_screenshot.entity import MissingScreenshot
from app.modules.runs.domains.run_counts.entity import RunCounts
from app.modules.runs.domains.run_report_story.entity import RunReportStory
from app.modules.runs.domains.skipped_run_case.entity import SkippedRunCase
from app.modules.runs.domains.unmapped_test.entity import UnmappedTest
from app.shared.common import Entity


class RunReport(Entity):
    counts: RunCounts
    failed_cases: list[FailedCaseReport]
    criterion_impacts: list[CriterionImpact]
    missing_screenshots: list[MissingScreenshot]
    summary: str | None
    built_at: datetime
    stories: list[RunReportStory] = Field(default_factory=list)
    skipped_cases: list[SkippedRunCase] = Field(default_factory=list)
    unmapped_tests: list[UnmappedTest] = Field(default_factory=list)
    unmapped_test_count: int = 0
