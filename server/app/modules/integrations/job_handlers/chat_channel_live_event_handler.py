from app.modules.integrations.usecases.request_chat_deliveries import RequestChatDeliveriesUseCase
from app.shared.events import LiveEvent, LiveEventHandler


class ChatChannelLiveEventHandler(LiveEventHandler):
    def __init__(self, use_case: RequestChatDeliveriesUseCase) -> None:
        self._use_case = use_case

    async def handle(self, event: LiveEvent) -> None:
        await self._use_case.execute(event)
