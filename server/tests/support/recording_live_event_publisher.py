from app.shared.events import LiveEvent, LiveEventPublisher


class RecordingLiveEventPublisher(LiveEventPublisher):
    def __init__(self) -> None:
        self.events: list[LiveEvent] = []

    async def publish(self, event: LiveEvent) -> None:
        self.events.append(event)

    async def close(self) -> None:
        return None
