from abc import ABC, abstractmethod
from uuid import UUID


class WebhookDeliveryRequester(ABC):
    @abstractmethod
    async def request(self, delivery_id: UUID) -> None: ...
