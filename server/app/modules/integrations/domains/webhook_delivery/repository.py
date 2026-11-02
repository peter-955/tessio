from abc import ABC, abstractmethod
from collections.abc import Collection
from datetime import datetime
from uuid import UUID

from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery


class WebhookDeliveryRepository(ABC):
    @abstractmethod
    async def find(self, webhook_id: UUID, delivery_id: UUID) -> WebhookDelivery | None: ...

    @abstractmethod
    async def find_for_update(self, delivery_id: UUID) -> WebhookDelivery | None: ...

    @abstractmethod
    async def list_for_webhook(self, webhook_id: UUID, limit: int) -> list[WebhookDelivery]: ...

    @abstractmethod
    async def map_latest(self, webhook_ids: Collection[UUID]) -> dict[UUID, WebhookDelivery]: ...

    @abstractmethod
    async def save(self, delivery: WebhookDelivery) -> None: ...

    @abstractmethod
    async def delete_created_before(self, cutoff: datetime) -> int: ...
