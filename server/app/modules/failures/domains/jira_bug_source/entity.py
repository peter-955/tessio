from uuid import UUID

from app.modules.runs import SuspectedCause
from app.modules.test_cases import TestStep
from app.shared.common import Entity


class JiraBugSource(Entity):
    failure_id: UUID
    project_key: str
    jira_project_key: str | None
    jira_bug_issue_type: str
    story_jira_key: str
    story_title: str
    is_story_from_jira: bool
    test_case_code: str
    test_case_title: str
    preconditions: str | None
    steps: list[TestStep]
    iteration: int
    data_row: dict[str, str] | None
    repro_steps: list[str] | None
    environment_id: UUID
    environment_name: str
    environment_base_url: str
    cause: SuspectedCause | None
    cause_reason: str | None
