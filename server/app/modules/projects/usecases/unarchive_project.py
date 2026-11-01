from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.domains.project_overview.entity import ProjectOverview
from app.modules.projects.utils.project_access import build_project_access
from app.shared.common import Transaction
from app.shared.permissions import (
    Actor,
    Capability,
    ProjectAccessResolver,
    ProjectNotFoundError,
    WorkspaceCapability,
    require,
    require_workspace,
)


class UnarchiveProjectUseCase:
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
            require_workspace(actor, WorkspaceCapability.PROJECT_ARCHIVE)
            project = await self._project_repository.find_by_id(access.project_id)
            if project is None:
                raise ProjectNotFoundError
            updated_project = project.model_copy(update={"archived_at": None})
            if updated_project != project:
                await self._project_repository.save(updated_project)
        return ProjectOverview(project=updated_project, access=build_project_access(updated_project, access.role))
