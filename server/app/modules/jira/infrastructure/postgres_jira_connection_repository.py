from sqlalchemy import update

from app.modules.jira.domains.jira_connection.entity import JiraConnection
from app.modules.jira.domains.jira_connection.repository import JiraConnectionRepository
from app.modules.jira.domains.jira_write_access.entity import JiraWriteAccess
from app.modules.jira.infrastructure.jira_connection_table import JiraConnectionTable
from app.modules.jira.typing.constants import JIRA_CONNECTION_ID
from app.shared.postgres import Database


class PostgresJiraConnectionRepository(JiraConnectionRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self) -> JiraConnection | None:
        row = await self._database.get_current_session().get(JiraConnectionTable, JIRA_CONNECTION_ID)
        return None if row is None else JiraConnection.model_validate(row)

    async def save(self, connection: JiraConnection) -> None:
        await self._database.get_current_session().merge(
            JiraConnectionTable(id=JIRA_CONNECTION_ID, **connection.model_dump())
        )

    async def save_write_access(self, write_access: JiraWriteAccess) -> None:
        await self._database.get_current_session().execute(
            update(JiraConnectionTable)
            .where(JiraConnectionTable.id == JIRA_CONNECTION_ID)
            .values(
                can_create_issues=write_access.can_create_issues,
                can_comment=write_access.can_comment,
                missing_permissions=[permission.value for permission in write_access.missing_permissions],
                permissions_checked_at=write_access.checked_at,
            )
        )
