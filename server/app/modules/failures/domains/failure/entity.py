from datetime import datetime
from uuid import UUID

from app.modules.failures.typing.constants import ACTIVE_FAILURE_STATUSES
from app.modules.failures.typing.enums import FailureStatus
from app.modules.runs import SuspectedCause
from app.shared.common import Entity
from app.shared.typing.enums import ErrorCode


class Failure(Entity):
    id: UUID
    project_id: UUID
    story_id: UUID
    test_case_id: UUID
    opened_by_case_result_id: UUID
    latest_case_result_id: UUID
    assignee_id: UUID | None
    status: FailureStatus
    status_changed_at: datetime | None
    status_changed_by: UUID | None
    cause: SuspectedCause | None
    cause_reason: str | None
    cause_changed_at: datetime | None
    cause_changed_by: UUID | None
    created_at: datetime
    jira_issue_key: str | None = None
    jira_issue_url: str | None = None
    jira_issue_status: str | None = None
    jira_issue_done_at: datetime | None = None
    jira_issue_requested_at: datetime | None = None
    jira_issue_error_code: ErrorCode | None = None

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_FAILURE_STATUSES

    @property
    def is_done_in_jira(self) -> bool:
        return self.jira_issue_done_at is not None

    @property
    def has_jira_issue(self) -> bool:
        return self.jira_issue_key is not None
