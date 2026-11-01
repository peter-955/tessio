from uuid import UUID

from sqlalchemy import select

from app.modules.test_cases.ports.data_key_reader import DataKeyReader
from app.modules.test_data.infrastructure import DataItemTable
from app.shared.postgres import Database


class PostgresDataKeyReader(DataKeyReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_keys(self, project_id: UUID) -> frozenset[str]:
        keys = await self._database.get_current_session().scalars(
            select(DataItemTable.key).where(DataItemTable.project_id == project_id).distinct()
        )
        return frozenset(keys)
