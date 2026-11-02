from uuid import UUID

from sqlalchemy import DateTime, String, Uuid, column, select, table

from app.modules.jira.ports.linked_project_reader import LinkedProjectReader
from app.shared.postgres import Database

PROJECTS = table(
    "projects",
    column("id", Uuid()),
    column("jira_project_key", String()),
    column("archived_at", DateTime(timezone=True)),
)


class PostgresLinkedProjectReader(LinkedProjectReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_linked_jira_project_keys(self) -> frozenset[str]:
        jira_project_keys = await self._database.get_current_session().scalars(select(PROJECTS.c.jira_project_key))
        return frozenset(str(jira_project_key) for jira_project_key in jira_project_keys)

    async def find_project_id_by_jira_project_key(self, jira_project_key: str) -> UUID | None:
        project_id: UUID | None = await self._database.get_current_session().scalar(
            select(PROJECTS.c.id).where(PROJECTS.c.jira_project_key == jira_project_key)
        )
        return project_id

    async def list_active_jira_project_keys(self) -> list[str]:
        jira_project_keys = await self._database.get_current_session().scalars(
            select(PROJECTS.c.jira_project_key)
            .where(PROJECTS.c.jira_project_key.is_not(None), PROJECTS.c.archived_at.is_(None))
            .order_by(PROJECTS.c.jira_project_key)
        )
        return [str(jira_project_key) for jira_project_key in jira_project_keys]

    async def find_jira_project_key(self, project_id: UUID) -> str | None:
        jira_project_key: str | None = await self._database.get_current_session().scalar(
            select(PROJECTS.c.jira_project_key).where(PROJECTS.c.id == project_id)
        )
        return jira_project_key
