from app.modules.jira.domains.jira_board.entity import JiraBoard
from app.modules.jira.domains.jira_connection.repository import JiraConnectionRepository
from app.modules.jira.errors import JiraNotConfiguredError
from app.modules.jira.ports.jira_client import JiraClient
from app.modules.jira.ports.linked_project_reader import LinkedProjectReader
from app.modules.jira.utils.jira_credentials import build_jira_credentials
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import (
    WORKSPACE_ROLE_CAPABILITIES,
    Actor,
    Capability,
    PermissionDeniedError,
    ProjectAccessResolver,
    WorkspaceCapability,
    require,
)


class ListJiraBoardsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        jira_connection_repository: JiraConnectionRepository,
        secret_cipher: SecretCipher,
        jira_client: JiraClient,
        linked_project_reader: LinkedProjectReader,
        project_access_resolver: ProjectAccessResolver,
    ) -> None:
        self._transaction = transaction
        self._jira_connection_repository = jira_connection_repository
        self._secret_cipher = secret_cipher
        self._jira_client = jira_client
        self._linked_project_reader = linked_project_reader
        self._project_access_resolver = project_access_resolver

    async def execute(self, actor: Actor, jira_project_key: str) -> list[JiraBoard]:
        async with self._transaction.begin():
            if WorkspaceCapability.PROJECT_CREATE not in WORKSPACE_ROLE_CAPABILITIES[actor.workspace_role]:
                await self._require_linked_project_edit(actor, jira_project_key)
            connection = await self._jira_connection_repository.find()
            if connection is None:
                raise JiraNotConfiguredError
        jira_boards = await self._jira_client.list_boards(
            build_jira_credentials(connection, self._secret_cipher), jira_project_key
        )
        return sorted(jira_boards, key=lambda jira_board: (jira_board.name.casefold(), jira_board.id))

    async def _require_linked_project_edit(self, actor: Actor, jira_project_key: str) -> None:
        project_id = await self._linked_project_reader.find_project_id_by_jira_project_key(jira_project_key)
        if project_id is None:
            raise PermissionDeniedError
        access = await self._project_access_resolver.resolve_by_id(actor, project_id)
        if access.role is None:
            raise PermissionDeniedError
        require(access, Capability.PROJECT_EDIT)
