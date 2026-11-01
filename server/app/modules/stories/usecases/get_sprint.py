from uuid import UUID

from app.modules.stories.domains.sprint.repository import SprintRepository
from app.modules.stories.domains.sprint_overview.entity import SprintOverview
from app.modules.stories.errors import SprintNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetSprintUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        sprint_repository: SprintRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._sprint_repository = sprint_repository

    async def execute(self, actor: Actor, project_key: str, sprint_id: UUID) -> SprintOverview:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.SPRINT_VIEW)
            overview = await self._sprint_repository.find_overview(access.project_id, sprint_id)
        if overview is None:
            raise SprintNotFoundError
        return overview
