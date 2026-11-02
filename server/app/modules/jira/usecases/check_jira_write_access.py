from datetime import datetime

from app.modules.jira.domains.jira_credentials.entity import JiraCredentials
from app.modules.jira.domains.jira_write_access.entity import JiraWriteAccess
from app.modules.jira.ports.jira_client import JiraClient
from app.modules.jira.ports.linked_project_reader import LinkedProjectReader
from app.modules.jira.typing.enums import JiraPermission
from app.modules.jira.utils.jira_write_access import build_jira_write_access
from app.shared.common import Transaction


class CheckJiraWriteAccessUseCase:
    def __init__(
        self, transaction: Transaction, linked_project_reader: LinkedProjectReader, jira_client: JiraClient
    ) -> None:
        self._transaction = transaction
        self._linked_project_reader = linked_project_reader
        self._jira_client = jira_client

    async def execute(self, credentials: JiraCredentials, now: datetime) -> JiraWriteAccess:
        async with self._transaction.begin():
            jira_project_keys = await self._linked_project_reader.list_active_jira_project_keys()
        missing_permissions: set[JiraPermission] = set()
        if not jira_project_keys:
            missing_permissions.update(await self._jira_client.list_missing_permissions(credentials, None))
        for jira_project_key in jira_project_keys:
            missing_permissions.update(await self._jira_client.list_missing_permissions(credentials, jira_project_key))
        return build_jira_write_access(missing_permissions, now)
