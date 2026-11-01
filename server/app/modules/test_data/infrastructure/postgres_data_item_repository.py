from uuid import UUID

from sqlalchemy import delete, or_, select

from app.modules.test_data.domains.data_item.entity import DataItem
from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.infrastructure.data_item_table import DataItemTable
from app.shared.postgres import Database


class PostgresDataItemRepository(DataItemRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, project_id: UUID, item_id: UUID) -> DataItem | None:
        row = await self._database.get_current_session().scalar(
            select(DataItemTable).where(DataItemTable.project_id == project_id, DataItemTable.id == item_id)
        )
        return None if row is None else DataItem.model_validate(row)

    async def find_by_key(self, project_id: UUID, environment_id: UUID | None, key: str) -> DataItem | None:
        row = await self._database.get_current_session().scalar(
            select(DataItemTable).where(
                DataItemTable.project_id == project_id,
                DataItemTable.environment_id.is_not_distinct_from(environment_id),
                DataItemTable.key == key,
            )
        )
        return None if row is None else DataItem.model_validate(row)

    async def list_for_environment(self, project_id: UUID, environment_id: UUID | None) -> list[DataItem]:
        scope = (
            DataItemTable.environment_id.is_(None)
            if environment_id is None
            else or_(DataItemTable.environment_id.is_(None), DataItemTable.environment_id == environment_id)
        )
        rows = await self._database.get_current_session().scalars(
            select(DataItemTable)
            .where(DataItemTable.project_id == project_id, scope)
            .order_by(DataItemTable.key, DataItemTable.environment_id.nulls_first(), DataItemTable.id)
        )
        return [DataItem.model_validate(row) for row in rows]

    async def list(self, project_id: UUID) -> list[DataItem]:
        rows = await self._database.get_current_session().scalars(
            select(DataItemTable)
            .where(DataItemTable.project_id == project_id)
            .order_by(DataItemTable.key, DataItemTable.environment_id.nulls_first(), DataItemTable.id)
        )
        return [DataItem.model_validate(row) for row in rows]

    async def save(self, item: DataItem) -> None:
        await self._database.get_current_session().merge(DataItemTable(**item.model_dump()))

    async def delete(self, item_id: UUID) -> None:
        await self._database.get_current_session().execute(delete(DataItemTable).where(DataItemTable.id == item_id))
