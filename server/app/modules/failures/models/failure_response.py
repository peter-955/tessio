from datetime import datetime
from uuid import UUID

from app.modules.failures.typing.enums import FailureStatus
from app.modules.users import UserStatus
from app.shared.common import WireModel


class FailureResponse(WireModel):
    id: UUID
    project_key: str
    story_id: UUID
    story_jira_key: str
    story_title: str
    test_case_id: UUID
    test_case_code: str
    test_case_title: str
    status: FailureStatus
    is_active: bool
    assignee_id: UUID | None
    assignee_name: str | None
    assignee_status: UserStatus | None
    opened_by_case_result_id: UUID
    latest_case_result_id: UUID
    latest_run_id: UUID
    latest_failed_at: datetime
    status_changed_at: datetime | None
    status_changed_by_name: str | None
    created_at: datetime
