from sqlalchemy.dialects.postgresql import insert

from app.modules.runs.domains.run_file.entity import RunFile
from app.modules.runs.domains.run_file.repository import RunFileRepository
from app.modules.runs.infrastructure.run_file_table import RunFileTable
from app.shared.postgres import Database


class PostgresRunFileRepository(RunFileRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def add(self, run_file: RunFile) -> None:
        await self._database.get_current_session().execute(
            insert(RunFileTable)
            .values(**run_file.model_dump())
            .on_conflict_do_nothing(index_elements=["run_id", "test_case_id", "key"])
        )
