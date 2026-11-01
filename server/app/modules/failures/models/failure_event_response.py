from datetime import datetime
from uuid import UUID

from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.shared.common import WireModel


class FailureEventResponse(WireModel):
    id: UUID
    kind: FailureEventKind
    from_status: FailureStatus | None
    to_status: FailureStatus | None
    case_result_id: UUID | None
    run_id: UUID | None
    assignee_id: UUID | None
    assignee_name: str | None
    actor_id: UUID | None
    actor_name: str | None
    created_at: datetime
