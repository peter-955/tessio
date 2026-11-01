from app.modules.jira.domains.jira_connection.repository import JiraConnectionRepository
from app.modules.jira.domains.jira_project.entity import JiraProject
from app.modules.jira.errors import JiraNotConfiguredError
from app.modules.jira.ports.jira_client import JiraClient
from app.modules.jira.ports.linked_project_reader import LinkedProjectReader
from app.modules.jira.utils.jira_credentials import build_jira_credentials
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class ListJiraProjectsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        jira_connection_repository: JiraConnectionRepository,
        secret_cipher: SecretCipher,
        jira_client: JiraClient,
        linked_project_reader: LinkedProjectReader,
    ) -> None:
        self._transaction = transaction
        self._jira_connection_repository = jira_connection_repository
        self._secret_cipher = secret_cipher
        self._jira_client = jira_client
        self._linked_project_reader = linked_project_reader

    async def execute(self, actor: Actor) -> list[JiraProject]:
        require_workspace(actor, WorkspaceCapability.PROJECT_CREATE)
        async with self._transaction.begin():
            connection = await self._jira_connection_repository.find()
            if connection is None:
                raise JiraNotConfiguredError
            linked_jira_project_keys = await self._linked_project_reader.list_linked_jira_project_keys()
        jira_projects = await self._jira_client.list_projects(build_jira_credentials(connection, self._secret_cipher))
        return sorted(
            (jira_project for jira_project in jira_projects if jira_project.key not in linked_jira_project_keys),
            key=lambda jira_project: (jira_project.name.casefold(), jira_project.key),
        )
