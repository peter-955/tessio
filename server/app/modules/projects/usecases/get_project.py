from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.domains.project_overview.entity import ProjectOverview
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class GetProjectUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        project_repository: ProjectRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._project_repository = project_repository

    async def execute(self, actor: Actor, key: str) -> ProjectOverview:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, key)
            require(access, Capability.PROJECT_VIEW)
            project = await self._project_repository.find_by_id(access.project_id)
            if project is None:
                raise ProjectNotFoundError
        return ProjectOverview(project=project, access=access)
