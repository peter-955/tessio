from app.modules.stories.domains.project_sync_state.entity import ProjectSyncState
from app.modules.stories.domains.project_sync_state.repository import ProjectSyncStateRepository
from app.modules.stories.typing.enums import ProjectSyncStatus
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetSyncStatusUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        project_sync_state_repository: ProjectSyncStateRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._project_sync_state_repository = project_sync_state_repository

    async def execute(self, actor: Actor, project_key: str) -> ProjectSyncState:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.SPRINT_VIEW)
            state = await self._project_sync_state_repository.find(access.project_id)
        if state is not None:
            return state
        return ProjectSyncState(
            project_id=access.project_id,
            status=ProjectSyncStatus.NEVER,
            requested_by=None,
            queued_at=None,
            started_at=None,
            finished_at=None,
            last_succeeded_at=None,
            error_code=None,
        )
