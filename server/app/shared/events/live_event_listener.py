import asyncio
from collections.abc import Sequence
from contextlib import suppress

from app.shared.events.live_event import LiveEvent
from app.shared.events.live_event_handler import LiveEventHandler
from app.shared.events.live_event_hub import LiveEventHub
from app.shared.logging import get_logger

log = get_logger(__name__)


class LiveEventListener:
    def __init__(self, hub: LiveEventHub, handlers: Sequence[LiveEventHandler]) -> None:
        self._hub = hub
        self._handlers = tuple(handlers)
        self._task: asyncio.Task[None] | None = None

    @property
    def is_listening(self) -> bool:
        return self._task is not None and not self._task.done()

    def start(self) -> None:
        if not self._handlers or self.is_listening:
            return
        self._task = asyncio.create_task(self._listen())

    async def close(self) -> None:
        task = self._task
        self._task = None
        if task is None:
            return
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

    async def _listen(self) -> None:
        async with self._hub.subscribe() as subscription:
            async for event in subscription:
                await self._dispatch(event)

    async def _dispatch(self, event: LiveEvent) -> None:
        for handler in self._handlers:
            try:
                await handler.handle(event)
            except Exception:
                log.exception(
                    "live_event.handler_failed",
                    extra={"event_type": event.type.value, "handler": type(handler).__name__},
                )
