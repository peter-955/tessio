from app.modules.integrations import IntegrationEvent
from app.modules.integrations.typing.constants import INTEGRATION_EVENT_BY_LIVE_EVENT


def test_every_integration_event_comes_from_exactly_one_live_event() -> None:
    assert sorted(INTEGRATION_EVENT_BY_LIVE_EVENT.values()) == sorted(IntegrationEvent)


def test_integration_events_keep_the_live_event_names() -> None:
    assert all(live_event.value == event.value for live_event, event in INTEGRATION_EVENT_BY_LIVE_EVENT.items())
