from collections.abc import Mapping

from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.shared.events import LiveEventType

INTEGRATION_EVENT_BY_LIVE_EVENT: Mapping[LiveEventType, IntegrationEvent] = {
    LiveEventType.RUN_STARTED: IntegrationEvent.RUN_STARTED,
    LiveEventType.RUN_FINISHED: IntegrationEvent.RUN_FINISHED,
    LiveEventType.FAILURE_OPENED: IntegrationEvent.FAILURE_OPENED,
    LiveEventType.FAILURE_STATUS_CHANGED: IntegrationEvent.FAILURE_STATUS_CHANGED,
    LiveEventType.GAP_RAISED: IntegrationEvent.GAP_RAISED,
    LiveEventType.STORY_SIGNED_OFF: IntegrationEvent.STORY_SIGNED_OFF,
    LiveEventType.PLAN_SIGNED_OFF: IntegrationEvent.PLAN_SIGNED_OFF,
}
