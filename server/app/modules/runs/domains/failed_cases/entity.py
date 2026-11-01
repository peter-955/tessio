from app.modules.runs.domains.failed_case.entity import FailedCase
from app.modules.runs.domains.run.entity import Run
from app.shared.common import Entity


class FailedCases(Entity):
    run: Run
    story_jira_key: str
    environment_name: str
    cases: list[FailedCase]
