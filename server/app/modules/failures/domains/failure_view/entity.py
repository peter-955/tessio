from datetime import datetime
from uuid import UUID

from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.typing.constants import TEST_CASE_CODE_PREFIX
from app.modules.users import UserStatus
from app.shared.common import Entity


class FailureView(Entity):
    failure: Failure
    project_key: str
    story_jira_key: str
    story_title: str
    test_case_number: int
    test_case_title: str
    assignee_name: str | None
    assignee_status: UserStatus | None
    status_changed_by_name: str | None
    latest_run_id: UUID
    latest_failed_at: datetime

    @property
    def test_case_code(self) -> str:
        return f"{TEST_CASE_CODE_PREFIX}{self.test_case_number}"
