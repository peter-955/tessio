from app.modules.shared_steps.domains.shared_step.repository import SharedStepRepository
from app.modules.shared_steps.domains.shared_step_detail.entity import SharedStepDetail
from app.modules.shared_steps.ports.shared_step_usage_reader import SharedStepUsageReader
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListSharedStepsUseCase:
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

    async def execute(self, actor: Actor, project_key: str, is_including_archived: bool) -> list[SharedStepDetail]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_VIEW)
            current_steps = await self._shared_step_repository.list_current(access.project_id, is_including_archived)
            usage_counts = await self._shared_step_usage_reader.count_cases(
                access.project_id, [current.shared_step.key for current in current_steps]
            )
        return [
            SharedStepDetail(
                shared_step=current.shared_step,
                version=current.version,
                usage_count=usage_counts.get(current.shared_step.key, 0),
            )
            for current in current_steps
        ]
