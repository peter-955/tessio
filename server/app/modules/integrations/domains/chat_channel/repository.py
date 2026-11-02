from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.integrations.domains.chat_channel.entity import ChatChannel
from app.modules.integrations.typing.enums import ChatDeliveryStatus, IntegrationEvent


class ChatChannelRepository(ABC):
    @abstractmethod
    async def list_for_project(self, project_id: UUID) -> list[ChatChannel]: ...

    @abstractmethod
    async def list_subscribed(self, project_id: UUID, event: IntegrationEvent) -> list[ChatChannel]: ...

    @abstractmethod
    async def find_by_id(self, project_id: UUID, chat_channel_id: UUID) -> ChatChannel | None: ...

    @abstractmethod
    async def find_any(self, chat_channel_id: UUID) -> ChatChannel | None: ...

    @abstractmethod
    async def find_by_name(self, project_id: UUID, name: str) -> ChatChannel | None: ...

    @abstractmethod
    async def count_for_project(self, project_id: UUID) -> int: ...

    @abstractmethod
    async def save(self, chat_channel: ChatChannel) -> None: ...

    @abstractmethod
    async def delete(self, chat_channel_id: UUID) -> None: ...

    @abstractmethod
    async def record_delivery(
        self, chat_channel_id: UUID, status: ChatDeliveryStatus, delivered_at: datetime, error: str | None
    ) -> None: ...
