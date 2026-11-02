from abc import ABC, abstractmethod

from app.shared.events.live_event import LiveEvent


class LiveEventHandler(ABC):
    @abstractmethod
    async def handle(self, event: LiveEvent) -> None: ...
