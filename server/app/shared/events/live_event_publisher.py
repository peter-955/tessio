from abc import ABC, abstractmethod

from app.shared.events.live_event import LiveEvent


class LiveEventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: LiveEvent) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...
