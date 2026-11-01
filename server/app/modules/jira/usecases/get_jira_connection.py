from app.modules.jira.domains.jira_connection.entity import JiraConnection
from app.modules.jira.domains.jira_connection.repository import JiraConnectionRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class GetJiraConnectionUseCase:
    def __init__(self, transaction: Transaction, jira_connection_repository: JiraConnectionRepository) -> None:
        self._transaction = transaction
        self._jira_connection_repository = jira_connection_repository

    async def execute(self, actor: Actor) -> JiraConnection | None:
        require_workspace(actor, WorkspaceCapability.JIRA_CONFIGURE)
        async with self._transaction.begin():
            return await self._jira_connection_repository.find()
