from uuid import UUID

from sqlalchemy import select

from app.modules.projects.domains.project.entity import Project
from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.infrastructure.project_table import ProjectTable
from app.shared.postgres import Database


class PostgresProjectRepository(ProjectRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_key(self, key: str) -> Project | None:
        row = await self._database.get_current_session().scalar(select(ProjectTable).where(ProjectTable.key == key))
        return None if row is None else Project.model_validate(row)

    async def find_by_key_for_update(self, key: str) -> Project | None:
        row = await self._database.get_current_session().scalar(
            select(ProjectTable)
            .where(ProjectTable.key == key)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else Project.model_validate(row)

    async def find_by_id(self, project_id: UUID) -> Project | None:
        row = await self._database.get_current_session().get(ProjectTable, project_id)
        return None if row is None else Project.model_validate(row)

    async def find_by_jira_project_key(self, jira_project_key: str) -> Project | None:
        row = await self._database.get_current_session().scalar(
            select(ProjectTable).where(ProjectTable.jira_project_key == jira_project_key)
        )
        return None if row is None else Project.model_validate(row)

    async def list(self, project_ids: frozenset[UUID] | None, is_including_archived: bool) -> list[Project]:
        statement = select(ProjectTable).order_by(ProjectTable.name, ProjectTable.key)
        if project_ids is not None:
            statement = statement.where(ProjectTable.id.in_(project_ids))
        if not is_including_archived:
            statement = statement.where(ProjectTable.archived_at.is_(None))
        rows = await self._database.get_current_session().scalars(statement)
        return [Project.model_validate(row) for row in rows]

    async def save(self, project: Project) -> None:
        await self._database.get_current_session().merge(ProjectTable(**project.model_dump()))
