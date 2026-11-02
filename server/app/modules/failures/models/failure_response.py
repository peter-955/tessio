from datetime import datetime
from uuid import UUID

from app.modules.failures.typing.enums import FailureStatus
from app.modules.runs import SuspectedCause
from app.modules.users import UserStatus
from app.shared.common import WireModel
from app.shared.typing.enums import ErrorCode


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
    cause: SuspectedCause | None
    cause_reason: str | None
    cause_changed_at: datetime | None
    created_at: datetime
    jira_issue_key: str | None
    jira_issue_url: str | None
    jira_issue_status: str | None
    jira_issue_done_at: datetime | None
    is_done_in_jira: bool
    is_jira_issue_pending: bool
    jira_issue_error_code: ErrorCode | None
