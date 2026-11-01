from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.failure_filter.entity import FailureFilter
from app.modules.failures.domains.failure_view.entity import FailureView
from app.modules.failures.errors import InvalidFailureFilterError
from app.modules.failures.typing.constants import MAX_FAILURE_LIST_SIZE
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListFailuresUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        failure_repository: FailureRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._failure_repository = failure_repository

    async def execute(self, actor: Actor, project_key: str, failure_filter: FailureFilter) -> list[FailureView]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.FAILURE_VIEW)
            if failure_filter.assignee_id is not None and failure_filter.is_unassigned:
                raise InvalidFailureFilterError
            views = await self._failure_repository.list_views(access.project_id, failure_filter, MAX_FAILURE_LIST_SIZE)
        return views
