from uuid import UUID

from app.modules.failures.domains.failure_event.entity import FailureEvent
from app.shared.common import Entity


class FailureEventView(Entity):
    event: FailureEvent
    run_id: UUID | None
    assignee_name: str | None
    actor_name: str | None
