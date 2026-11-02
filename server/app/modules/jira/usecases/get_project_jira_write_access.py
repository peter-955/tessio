from app.modules.jira.domains.jira_connection.repository import JiraConnectionRepository
from app.modules.jira.domains.project_jira_write_access.entity import ProjectJiraWriteAccess
from app.modules.jira.ports.linked_project_reader import LinkedProjectReader
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetProjectJiraWriteAccessUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        linked_project_reader: LinkedProjectReader,
        jira_connection_repository: JiraConnectionRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._linked_project_reader = linked_project_reader
        self._jira_connection_repository = jira_connection_repository

    async def execute(self, actor: Actor, project_key: str) -> ProjectJiraWriteAccess:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.PROJECT_VIEW)
            jira_project_key = await self._linked_project_reader.find_jira_project_key(access.project_id)
            connection = await self._jira_connection_repository.find()
        return ProjectJiraWriteAccess(
            is_project_linked=jira_project_key is not None,
            is_connection_configured=connection is not None,
            write_access=None if connection is None or jira_project_key is None else connection.write_access,
        )
