from datetime import datetime
from uuid import UUID

from app.modules.test_cases.typing.enums import QuarantineEventKind
from app.shared.common import WireModel


class QuarantineEventResponse(WireModel):
    id: UUID
    kind: QuarantineEventKind
    actor_id: UUID | None
    actor_name: str | None
    reason: str | None
    created_at: datetime
