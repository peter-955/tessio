from uuid import UUID

from sqlalchemy import select

from app.modules.projects.ports.environment_checker import EnvironmentChecker
from app.modules.test_data.infrastructure.environment_table import EnvironmentTable
from app.shared.postgres import Database


class PostgresEnvironmentChecker(EnvironmentChecker):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def is_active_environment(self, project_id: UUID, environment_id: UUID) -> bool:
        found_id = await self._database.get_current_session().scalar(
            select(EnvironmentTable.id).where(
                EnvironmentTable.id == environment_id,
                EnvironmentTable.project_id == project_id,
                EnvironmentTable.archived_at.is_(None),
            )
        )
        return found_id is not None
