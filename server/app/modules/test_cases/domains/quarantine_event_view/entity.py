from app.modules.test_cases.domains.quarantine_event.entity import QuarantineEvent
from app.shared.common import Entity


class QuarantineEventView(Entity):
    event: QuarantineEvent
    actor_name: str | None
