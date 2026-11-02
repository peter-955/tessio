from uuid import UUID

from sqlalchemy import ColumnElement, and_, delete, func, or_, select

from app.modules.test_data.domains.data_item.entity import DataItem
from app.modules.test_data.domains.data_item.repository import DataItemRepository
from app.modules.test_data.infrastructure.data_item_table import DataItemTable
from app.modules.test_data.infrastructure.data_key_description_table import DataKeyDescriptionTable
from app.shared.postgres import Database


async def load_data_items(database: Database, *conditions: ColumnElement[bool]) -> list[DataItem]:
    result = await database.get_current_session().execute(
        select(DataItemTable, DataKeyDescriptionTable.description)
        .outerjoin(
            DataKeyDescriptionTable,
            and_(
                DataKeyDescriptionTable.project_id == DataItemTable.project_id,
                DataKeyDescriptionTable.key == DataItemTable.key,
            ),
        )
        .where(*conditions)
        .order_by(DataItemTable.key, DataItemTable.environment_id.nulls_first(), DataItemTable.id)
    )
    return [build_data_item(row, description) for row, description in result]


def build_data_item(row: DataItemTable, description: str | None) -> DataItem:
    return DataItem.model_validate(row).model_copy(update={"description": description})


class PostgresDataItemRepository(DataItemRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, project_id: UUID, item_id: UUID) -> DataItem | None:
        items = await load_data_items(
            self._database, DataItemTable.project_id == project_id, DataItemTable.id == item_id
        )
        return items[0] if items else None

    async def find_by_key(self, project_id: UUID, environment_id: UUID | None, key: str) -> DataItem | None:
        items = await load_data_items(
            self._database,
            DataItemTable.project_id == project_id,
            DataItemTable.environment_id.is_not_distinct_from(environment_id),
            DataItemTable.key == key,
        )
        return items[0] if items else None

    async def list_for_environment(self, project_id: UUID, environment_id: UUID | None) -> list[DataItem]:
        scope = (
            DataItemTable.environment_id.is_(None)
            if environment_id is None
            else or_(DataItemTable.environment_id.is_(None), DataItemTable.environment_id == environment_id)
        )
        return await load_data_items(self._database, DataItemTable.project_id == project_id, scope)

    async def list(self, project_id: UUID) -> list[DataItem]:
        return await load_data_items(self._database, DataItemTable.project_id == project_id)

    async def count_by_key(self, project_id: UUID, key: str) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count())
            .select_from(DataItemTable)
            .where(DataItemTable.project_id == project_id, DataItemTable.key == key)
        )
        return int(count or 0)

    async def save(self, item: DataItem) -> None:
        await self._database.get_current_session().merge(DataItemTable(**item.model_dump(exclude={"description"})))

    async def delete(self, item_id: UUID) -> None:
        await self._database.get_current_session().execute(delete(DataItemTable).where(DataItemTable.id == item_id))
