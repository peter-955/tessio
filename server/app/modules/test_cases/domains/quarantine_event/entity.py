from datetime import datetime
from uuid import UUID

from app.modules.test_cases.typing.enums import QuarantineEventKind
from app.shared.common import Entity


class QuarantineEvent(Entity):
    id: UUID
    test_case_id: UUID
    kind: QuarantineEventKind
    actor_id: UUID | None
    reason: str | None
    created_at: datetime
