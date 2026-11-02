from pydantic import Field

from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.skipped_run_case.entity import SkippedRunCase
from app.modules.test_cases import TestCaseVersion
from app.shared.common import Entity


class RunSheet(Entity):
    run: Run
    story_jira_key: str | None
    case_versions: list[TestCaseVersion]
    case_results: list[CaseResult]
    suite_name: str | None = None
    skipped_cases: list[SkippedRunCase] = Field(default_factory=list)
