from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.test_data import Environment
from app.shared.common import Entity


class StartedRun(Entity):
    run: Run
    environment: Environment
    cases: list[RunCaseView]
