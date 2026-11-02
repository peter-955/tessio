from pydantic import Field

from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.domains.skipped_run_case.entity import SkippedRunCase
from app.modules.test_data import Environment
from app.shared.common import Entity


class StartedRun(Entity):
    run: Run
    environment: Environment
    cases: list[RunCaseView]
    suite_name: str | None = None
    skipped_cases: list[SkippedRunCase] = Field(default_factory=list)
