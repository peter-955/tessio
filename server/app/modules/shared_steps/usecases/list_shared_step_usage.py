from app.modules.shared_steps.domains.shared_step.repository import SharedStepRepository
from app.modules.shared_steps.domains.shared_step_usage.entity import SharedStepUsage
from app.modules.shared_steps.ports.shared_step_usage_reader import SharedStepUsageReader
from app.modules.shared_steps.utils.shared_step_lookup import require_shared_step
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListSharedStepUsageUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        shared_step_repository: SharedStepRepository,
        shared_step_usage_reader: SharedStepUsageReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._shared_step_repository = shared_step_repository
        self._shared_step_usage_reader = shared_step_usage_reader

    async def execute(self, actor: Actor, project_key: str, key: str) -> list[SharedStepUsage]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_VIEW)
            shared_step = await require_shared_step(self._shared_step_repository, access.project_id, key)
            return await self._shared_step_usage_reader.list_cases(access.project_id, shared_step.key)
