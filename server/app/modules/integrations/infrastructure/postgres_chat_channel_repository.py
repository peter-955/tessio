from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select, update

from app.modules.integrations.domains.chat_channel.entity import ChatChannel
from app.modules.integrations.domains.chat_channel.repository import ChatChannelRepository
from app.modules.integrations.infrastructure.project_chat_channel_table import ProjectChatChannelTable
from app.modules.integrations.typing.enums import ChatDeliveryStatus, IntegrationEvent
from app.shared.postgres import Database


class PostgresChatChannelRepository(ChatChannelRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_for_project(self, project_id: UUID) -> list[ChatChannel]:
        rows = await self._database.get_current_session().scalars(
            select(ProjectChatChannelTable)
            .where(ProjectChatChannelTable.project_id == project_id)
            .order_by(func.lower(ProjectChatChannelTable.name), ProjectChatChannelTable.id)
            .execution_options(populate_existing=True)
        )
        return [ChatChannel.model_validate(row) for row in rows]

    async def list_subscribed(self, project_id: UUID, event: IntegrationEvent) -> list[ChatChannel]:
        rows = await self._database.get_current_session().scalars(
            select(ProjectChatChannelTable)
            .where(
                ProjectChatChannelTable.project_id == project_id,
                ProjectChatChannelTable.is_active.is_(True),
                ProjectChatChannelTable.events.contains([event.value]),
            )
            .order_by(ProjectChatChannelTable.id)
            .execution_options(populate_existing=True)
        )
        return [ChatChannel.model_validate(row) for row in rows]

    async def find_by_id(self, project_id: UUID, chat_channel_id: UUID) -> ChatChannel | None:
        row = await self._database.get_current_session().scalar(
            select(ProjectChatChannelTable)
            .where(ProjectChatChannelTable.project_id == project_id, ProjectChatChannelTable.id == chat_channel_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else ChatChannel.model_validate(row)

    async def find_any(self, chat_channel_id: UUID) -> ChatChannel | None:
        row = await self._database.get_current_session().scalar(
            select(ProjectChatChannelTable)
            .where(ProjectChatChannelTable.id == chat_channel_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else ChatChannel.model_validate(row)

    async def find_by_name(self, project_id: UUID, name: str) -> ChatChannel | None:
        row = await self._database.get_current_session().scalar(
            select(ProjectChatChannelTable)
            .where(
                ProjectChatChannelTable.project_id == project_id,
                func.lower(ProjectChatChannelTable.name) == name.lower(),
            )
            .order_by(ProjectChatChannelTable.id)
            .limit(1)
            .execution_options(populate_existing=True)
        )
        return None if row is None else ChatChannel.model_validate(row)

    async def count_for_project(self, project_id: UUID) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count())
            .select_from(ProjectChatChannelTable)
            .where(ProjectChatChannelTable.project_id == project_id)
        )
        return int(count or 0)

    async def save(self, chat_channel: ChatChannel) -> None:
        values = chat_channel.model_dump()
        values["events"] = [event.value for event in chat_channel.events]
        await self._database.get_current_session().merge(ProjectChatChannelTable(**values))

    async def delete(self, chat_channel_id: UUID) -> None:
        await self._database.get_current_session().execute(
            delete(ProjectChatChannelTable).where(ProjectChatChannelTable.id == chat_channel_id)
        )

    async def record_delivery(
        self, chat_channel_id: UUID, status: ChatDeliveryStatus, delivered_at: datetime, error: str | None
    ) -> None:
        await self._database.get_current_session().execute(
            update(ProjectChatChannelTable)
            .where(ProjectChatChannelTable.id == chat_channel_id)
            .values(last_delivery_status=status, last_delivery_at=delivered_at, last_delivery_error=error)
        )
