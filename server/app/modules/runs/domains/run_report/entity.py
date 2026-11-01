from datetime import datetime

from app.modules.runs.domains.criterion_impact.entity import CriterionImpact
from app.modules.runs.domains.failed_case_report.entity import FailedCaseReport
from app.modules.runs.domains.missing_screenshot.entity import MissingScreenshot
from app.modules.runs.domains.run_counts.entity import RunCounts
from app.shared.common import Entity


class RunReport(Entity):
    counts: RunCounts
    failed_cases: list[FailedCaseReport]
    criterion_impacts: list[CriterionImpact]
    missing_screenshots: list[MissingScreenshot]
    summary: str | None
    built_at: datetime
