from app.modules.test_cases.domains.quarantine_event_view.entity import QuarantineEventView
from app.modules.test_cases.models.quarantine_event_response import QuarantineEventResponse


def build_quarantine_event_response(view: QuarantineEventView) -> QuarantineEventResponse:
    event = view.event
    return QuarantineEventResponse(
        id=event.id,
        kind=event.kind,
        actor_id=event.actor_id,
        actor_name=view.actor_name,
        reason=event.reason,
        created_at=event.created_at,
    )
