from datetime import UTC, datetime

from pydantic import SecretStr

from app.modules.jira.domains.jira_connection.entity import JiraConnection
from app.modules.jira.domains.jira_connection.repository import JiraConnectionRepository
from app.modules.jira.domains.jira_credentials.entity import JiraCredentials
from app.modules.jira.errors import JiraApiTokenRequiredError
from app.modules.jira.ports.jira_client import JiraClient
from app.modules.jira.utils.jira_credentials import build_jira_credentials
from app.modules.jira.utils.site_url import normalize_site_url
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class SaveJiraConnectionUseCase:
    def __init__(
        self,
        transaction: Transaction,
        jira_connection_repository: JiraConnectionRepository,
        jira_client: JiraClient,
        secret_cipher: SecretCipher,
    ) -> None:
        self._transaction = transaction
        self._jira_connection_repository = jira_connection_repository
        self._jira_client = jira_client
        self._secret_cipher = secret_cipher

    async def execute(
        self, actor: Actor, site_url: str, account_email: str, api_token: SecretStr | None
    ) -> JiraConnection:
        require_workspace(actor, WorkspaceCapability.JIRA_CONFIGURE)
        normalized_site_url = normalize_site_url(site_url)
        normalized_account_email = account_email.strip().lower()
        async with self._transaction.begin():
            existing_connection = await self._jira_connection_repository.find()
        credentials = JiraCredentials(
            site_url=normalized_site_url,
            account_email=normalized_account_email,
            api_token=self._resolve_api_token(api_token, existing_connection, normalized_site_url),
        )
        account = await self._jira_client.get_myself(credentials)
        connection = JiraConnection(
            site_url=normalized_site_url,
            account_email=normalized_account_email,
            api_token_encrypted=self._secret_cipher.encrypt(credentials.api_token.get_secret_value().encode()),
            account_id=account.account_id,
            account_display_name=account.display_name,
            configured_by=actor.user_id,
            configured_at=datetime.now(UTC),
        )
        async with self._transaction.begin():
            await self._jira_connection_repository.save(connection)
        return connection

    def _resolve_api_token(
        self, api_token: SecretStr | None, existing_connection: JiraConnection | None, site_url: str
    ) -> SecretStr:
        if api_token is not None:
            return api_token
        if existing_connection is None or existing_connection.site_url != site_url:
            raise JiraApiTokenRequiredError
        return build_jira_credentials(existing_connection, self._secret_cipher).api_token
