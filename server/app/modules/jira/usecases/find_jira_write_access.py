from app.modules.jira.domains.jira_connection.repository import JiraConnectionRepository
from app.modules.jira.domains.jira_write_access.entity import JiraWriteAccess
from app.shared.common import Transaction


class FindJiraWriteAccessUseCase:
    def __init__(self, transaction: Transaction, jira_connection_repository: JiraConnectionRepository) -> None:
        self._transaction = transaction
        self._jira_connection_repository = jira_connection_repository

    async def execute(self) -> JiraWriteAccess | None:
        async with self._transaction.begin():
            connection = await self._jira_connection_repository.find()
        return None if connection is None else connection.write_access
