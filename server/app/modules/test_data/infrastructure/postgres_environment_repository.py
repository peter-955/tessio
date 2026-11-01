from uuid import UUID

from sqlalchemy import delete, func, select, update

from app.modules.projects.infrastructure import ProjectTable
from app.modules.test_data.domains.environment.entity import Environment
from app.modules.test_data.domains.environment.repository import EnvironmentRepository
from app.modules.test_data.infrastructure.environment_table import EnvironmentTable
from app.shared.postgres import Database


class PostgresEnvironmentRepository(EnvironmentRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, project_id: UUID, environment_id: UUID) -> Environment | None:
        row = await self._database.get_current_session().scalar(
            select(EnvironmentTable).where(
                EnvironmentTable.project_id == project_id, EnvironmentTable.id == environment_id
            )
        )
        return None if row is None else Environment.model_validate(row)

    async def find_by_name(self, project_id: UUID, name: str) -> Environment | None:
        row = await self._database.get_current_session().scalar(
            select(EnvironmentTable)
            .where(EnvironmentTable.project_id == project_id, func.lower(EnvironmentTable.name) == name.lower())
            .order_by(EnvironmentTable.id)
            .limit(1)
        )
        return None if row is None else Environment.model_validate(row)

    async def list(self, project_id: UUID, is_including_archived: bool) -> list[Environment]:
        statement = (
            select(EnvironmentTable)
            .where(EnvironmentTable.project_id == project_id)
            .order_by(func.lower(EnvironmentTable.name), EnvironmentTable.name, EnvironmentTable.id)
        )
        if not is_including_archived:
            statement = statement.where(EnvironmentTable.archived_at.is_(None))
        rows = await self._database.get_current_session().scalars(statement)
        return [Environment.model_validate(row) for row in rows]

    async def save(self, environment: Environment) -> None:
        await self._database.get_current_session().merge(EnvironmentTable(**environment.model_dump()))

    async def delete(self, environment_id: UUID) -> None:
        await self._database.get_current_session().execute(
            delete(EnvironmentTable).where(EnvironmentTable.id == environment_id)
        )

    async def clear_project_default(self, environment_id: UUID) -> None:
        await self._database.get_current_session().execute(
            update(ProjectTable)
            .where(ProjectTable.default_environment_id == environment_id)
            .values(default_environment_id=None)
        )
