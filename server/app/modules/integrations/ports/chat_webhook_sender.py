from abc import ABC, abstractmethod

from pydantic import JsonValue


class ChatWebhookSender(ABC):
    @abstractmethod
    async def send(self, webhook_url: str, payload: dict[str, JsonValue]) -> None: ...
