from datetime import datetime

from app.modules.jira.domains.jira_connection.repository import JiraConnectionRepository
from app.modules.jira.domains.jira_write_access.entity import JiraWriteAccess
from app.modules.jira.usecases.check_jira_write_access import CheckJiraWriteAccessUseCase
from app.modules.jira.utils.jira_credentials import build_jira_credentials
from app.shared.common import TessioError, Transaction
from app.shared.crypto import SecretCipher
from app.shared.logging import get_logger

log = get_logger(__name__)


class RefreshJiraWriteAccessUseCase:
    def __init__(
        self,
        transaction: Transaction,
        jira_connection_repository: JiraConnectionRepository,
        secret_cipher: SecretCipher,
        check_jira_write_access: CheckJiraWriteAccessUseCase,
    ) -> None:
        self._transaction = transaction
        self._jira_connection_repository = jira_connection_repository
        self._secret_cipher = secret_cipher
        self._check_jira_write_access = check_jira_write_access

    async def execute(self, now: datetime) -> JiraWriteAccess | None:
        async with self._transaction.begin():
            connection = await self._jira_connection_repository.find()
        if connection is None:
            return None
        try:
            credentials = build_jira_credentials(connection, self._secret_cipher)
            write_access = await self._check_jira_write_access.execute(credentials, now)
        except TessioError as error:
            log.warning("jira.write_access.check_failed", extra={"error_code": error.code.value})
            return None
        async with self._transaction.begin():
            await self._jira_connection_repository.save_write_access(write_access)
        return write_access
