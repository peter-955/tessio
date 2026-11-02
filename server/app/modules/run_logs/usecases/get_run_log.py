from uuid import UUID

from app.modules.run_logs.domains.run_log.repository import RunLogRepository
from app.modules.run_logs.domains.run_log_view.entity import RunLogView
from app.modules.run_logs.errors import RunNotFoundError
from app.modules.runs import RunRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetRunLogUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_log_repository: RunLogRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_log_repository = run_log_repository

    async def execute(self, actor: Actor, project_key: str, run_id: UUID, test_case_id: UUID | None) -> RunLogView:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.RUN_VIEW)
            run = await self._run_repository.find_by_id(access.project_id, run_id)
            if run is None:
                raise RunNotFoundError
            run_log = await self._run_log_repository.find(run.id)
            entries = [] if run_log is None else await self._run_log_repository.list_entries(run.id, test_case_id)
        return RunLogView(run_log=run_log, entries=entries)
