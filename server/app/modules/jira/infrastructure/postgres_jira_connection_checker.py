from sqlalchemy import select

from app.modules.jira.infrastructure.jira_connection_table import JiraConnectionTable
from app.modules.jira.typing.constants import JIRA_CONNECTION_ID
from app.modules.projects import JiraConnectionChecker
from app.shared.postgres import Database


class PostgresJiraConnectionChecker(JiraConnectionChecker):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def is_configured(self) -> bool:
        async with self._database.begin():
            connection_id = await self._database.get_current_session().scalar(
                select(JiraConnectionTable.id).where(JiraConnectionTable.id == JIRA_CONNECTION_ID)
            )
        return connection_id is not None
