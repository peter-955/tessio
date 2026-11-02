from datetime import datetime
from uuid import UUID

from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.runs import SuspectedCause
from app.shared.common import Entity
from app.shared.typing.enums import ErrorCode


class FailureEvent(Entity):
    id: UUID
    failure_id: UUID
    kind: FailureEventKind
    from_status: FailureStatus | None
    to_status: FailureStatus | None
    from_cause: SuspectedCause | None = None
    to_cause: SuspectedCause | None = None
    case_result_id: UUID | None
    assignee_id: UUID | None
    actor_id: UUID | None
    created_at: datetime
    jira_issue_key: str | None = None
    error_code: ErrorCode | None = None
