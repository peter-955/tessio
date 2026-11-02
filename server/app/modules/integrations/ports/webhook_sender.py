from abc import ABC, abstractmethod
from collections.abc import Mapping

from app.modules.integrations.domains.webhook_send_result.entity import WebhookSendResult


class WebhookSender(ABC):
    @abstractmethod
    async def send(self, url: str, body: bytes, headers: Mapping[str, str]) -> WebhookSendResult: ...
