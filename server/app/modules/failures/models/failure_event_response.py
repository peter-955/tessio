from datetime import datetime
from uuid import UUID

from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.runs import SuspectedCause
from app.shared.common import WireModel
from app.shared.typing.enums import ErrorCode


class FailureEventResponse(WireModel):
    id: UUID
    kind: FailureEventKind
    from_status: FailureStatus | None
    to_status: FailureStatus | None
    from_cause: SuspectedCause | None
    to_cause: SuspectedCause | None
    case_result_id: UUID | None
    run_id: UUID | None
    assignee_id: UUID | None
    assignee_name: str | None
    actor_id: UUID | None
    actor_name: str | None
    created_at: datetime
    jira_issue_key: str | None
    error_code: ErrorCode | None
