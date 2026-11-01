import asyncio
from typing import Self

from app.shared.events.live_event import LiveEvent
from app.shared.events.live_event_constant import SUBSCRIPTION_BUFFER_SIZE
from app.shared.logging import get_logger

log = get_logger(__name__)


class LiveEventSubscription:
    def __init__(self, buffer_size: int = SUBSCRIPTION_BUFFER_SIZE) -> None:
        self._queue: asyncio.Queue[LiveEvent] = asyncio.Queue(maxsize=buffer_size)

    def deliver(self, event: LiveEvent) -> None:
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            log.warning("live_event.dropped", extra={"event_type": event.type.value})
        except asyncio.QueueShutDown:
            return

    def close(self) -> None:
        self._queue.shutdown()

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> LiveEvent:
        try:
            return await self._queue.get()
        except asyncio.QueueShutDown:
            raise StopAsyncIteration from None
