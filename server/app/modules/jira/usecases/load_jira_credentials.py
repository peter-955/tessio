from app.modules.jira.domains.jira_connection.repository import JiraConnectionRepository
from app.modules.jira.domains.jira_credentials.entity import JiraCredentials
from app.modules.jira.errors import JiraNotConfiguredError
from app.modules.jira.utils.jira_credentials import build_jira_credentials
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher


class LoadJiraCredentialsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        jira_connection_repository: JiraConnectionRepository,
        secret_cipher: SecretCipher,
    ) -> None:
        self._transaction = transaction
        self._jira_connection_repository = jira_connection_repository
        self._secret_cipher = secret_cipher

    async def execute(self) -> JiraCredentials:
        async with self._transaction.begin():
            connection = await self._jira_connection_repository.find()
        if connection is None:
            raise JiraNotConfiguredError
        return build_jira_credentials(connection, self._secret_cipher)
