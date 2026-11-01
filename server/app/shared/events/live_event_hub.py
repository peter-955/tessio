from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from app.shared.events.live_event_subscription import LiveEventSubscription


class LiveEventHub(ABC):
    @abstractmethod
    def subscribe(self) -> AbstractAsyncContextManager[LiveEventSubscription]: ...

    @abstractmethod
    async def close(self) -> None: ...
