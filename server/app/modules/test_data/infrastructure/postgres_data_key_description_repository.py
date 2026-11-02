from uuid import UUID

from sqlalchemy import delete, select

from app.modules.test_data.domains.data_key_description.repository import DataKeyDescriptionRepository
from app.modules.test_data.infrastructure.data_key_description_table import DataKeyDescriptionTable
from app.shared.postgres import Database


class PostgresDataKeyDescriptionRepository(DataKeyDescriptionRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self, project_id: UUID, key: str) -> str | None:
        description: str | None = await self._database.get_current_session().scalar(
            select(DataKeyDescriptionTable.description).where(
                DataKeyDescriptionTable.project_id == project_id, DataKeyDescriptionTable.key == key
            )
        )
        return description

    async def save(self, project_id: UUID, key: str, description: str) -> None:
        await self._database.get_current_session().merge(
            DataKeyDescriptionTable(project_id=project_id, key=key, description=description)
        )

    async def delete(self, project_id: UUID, key: str) -> None:
        await self._database.get_current_session().execute(
            delete(DataKeyDescriptionTable).where(
                DataKeyDescriptionTable.project_id == project_id, DataKeyDescriptionTable.key == key
            )
        )
