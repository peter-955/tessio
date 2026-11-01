from uuid import UUID

from sqlalchemy import exists, select

from app.modules.runs.infrastructure.run_table import RunTable
from app.modules.test_data import EnvironmentUsageChecker
from app.shared.postgres import Database


class PostgresEnvironmentUsageChecker(EnvironmentUsageChecker):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def is_used_by_runs(self, environment_id: UUID) -> bool:
        async with self._database.begin():
            is_used = await self._database.get_current_session().scalar(
                select(exists().where(RunTable.environment_id == environment_id))
            )
        return bool(is_used)
