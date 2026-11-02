from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.integrations.domains.webhook.entity import Webhook
from app.modules.integrations.typing.enums.integration_event import IntegrationEvent


class WebhookRepository(ABC):
    @abstractmethod
    async def find(self, project_id: UUID, webhook_id: UUID) -> Webhook | None: ...

    @abstractmethod
    async def find_by_id(self, webhook_id: UUID) -> Webhook | None: ...

    @abstractmethod
    async def list_for_project(self, project_id: UUID) -> list[Webhook]: ...

    @abstractmethod
    async def list_active_for_event(self, project_id: UUID, event: IntegrationEvent) -> list[Webhook]: ...

    @abstractmethod
    async def count_for_project(self, project_id: UUID) -> int: ...

    @abstractmethod
    async def save(self, webhook: Webhook) -> None: ...

    @abstractmethod
    async def delete(self, webhook_id: UUID) -> None: ...
