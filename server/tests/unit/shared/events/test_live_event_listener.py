import asyncio
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.shared.events import LiveEvent, LiveEventHandler, LiveEventHub, LiveEventListener, LiveEventType
from app.shared.events.live_event_subscription import LiveEventSubscription

WAIT_SECONDS = 2


class InMemoryLiveEventHub(LiveEventHub):
    def __init__(self) -> None:
        self.subscriptions: list[LiveEventSubscription] = []
        self.subscribed = asyncio.Event()

    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[LiveEventSubscription]:
        subscription = LiveEventSubscription()
        self.subscriptions.append(subscription)
        self.subscribed.set()
        try:
            yield subscription
        finally:
            self.subscriptions.remove(subscription)
            subscription.close()

    def deliver(self, event: LiveEvent) -> None:
        for subscription in self.subscriptions:
            subscription.deliver(event)

    async def close(self) -> None:
        return


class RecordingHandler(LiveEventHandler):
    def __init__(self, expected_count: int) -> None:
        self.events: list[LiveEvent] = []
        self._expected_count = expected_count
        self.done = asyncio.Event()

    async def handle(self, event: LiveEvent) -> None:
        self.events.append(event)
        if len(self.events) >= self._expected_count:
            self.done.set()


class FailingHandler(LiveEventHandler):
    async def handle(self, event: LiveEvent) -> None:
        raise RuntimeError(f"cannot handle {event.type.value}")


def build_event(event_type: LiveEventType) -> LiveEvent:
    return LiveEvent(type=event_type, project_id=uuid.uuid4())


async def test_listener_hands_every_event_to_every_handler_even_when_one_fails() -> None:
    hub = InMemoryLiveEventHub()
    recording_handler = RecordingHandler(expected_count=2)
    listener = LiveEventListener(hub, [FailingHandler(), recording_handler])
    events = [build_event(LiveEventType.RUN_FINISHED), build_event(LiveEventType.PLAN_SIGNED_OFF)]

    listener.start()
    try:
        await asyncio.wait_for(hub.subscribed.wait(), WAIT_SECONDS)
        for event in events:
            hub.deliver(event)
        await asyncio.wait_for(recording_handler.done.wait(), WAIT_SECONDS)
    finally:
        await listener.close()

    assert recording_handler.events == events
    assert hub.subscriptions == []
    assert listener.is_listening is False


async def test_listener_without_handlers_never_subscribes() -> None:
    hub = InMemoryLiveEventHub()
    listener = LiveEventListener(hub, [])

    listener.start()
    await asyncio.sleep(0)
    await listener.close()

    assert hub.subscribed.is_set() is False
    assert listener.is_listening is False
