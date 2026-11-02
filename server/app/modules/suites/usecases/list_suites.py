from app.modules.suites.domains.suite_summary.entity import SuiteSummary
from app.modules.suites.ports.suite_view_reader import SuiteViewReader
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListSuitesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        suite_view_reader: SuiteViewReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._suite_view_reader = suite_view_reader

    async def execute(self, actor: Actor, project_key: str, is_including_archived: bool) -> list[SuiteSummary]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_VIEW)
            summaries = await self._suite_view_reader.list_summaries(access.project_id, is_including_archived)
        return summaries
