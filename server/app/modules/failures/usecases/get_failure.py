from uuid import UUID

from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_detail.entity import FailureDetail
from app.modules.failures.domains.failure_event.repository import FailureEventRepository
from app.modules.failures.errors import FailureNotFoundError
from app.modules.failures.ports.case_result_reader import CaseResultReader
from app.modules.failures.typing.constants import MAX_RESULT_HISTORY_SIZE
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetFailureUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        failure_repository: FailureRepository,
        failure_event_repository: FailureEventRepository,
        case_result_reader: CaseResultReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._failure_repository = failure_repository
        self._failure_event_repository = failure_event_repository
        self._case_result_reader = case_result_reader

    async def execute(self, actor: Actor, project_key: str, failure_id: UUID) -> FailureDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.FAILURE_VIEW)
            view = await self._failure_repository.find_view(access.project_id, failure_id)
            if view is None:
                raise FailureNotFoundError
            failure = view.failure
            failed_step = await self._case_result_reader.find_failed_step(failure.latest_case_result_id)
            results = await self._case_result_reader.list_history(
                failure.test_case_id, failure.opened_by_case_result_id, MAX_RESULT_HISTORY_SIZE
            )
            events = await self._failure_event_repository.list_views(failure.id)
        return FailureDetail(view=view, failed_step=failed_step, results=results, events=events)
