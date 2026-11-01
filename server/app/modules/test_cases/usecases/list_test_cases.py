from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_filter.entity import TestCaseFilter
from app.modules.test_cases.domains.test_case_summary.entity import TestCaseSummary
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListTestCasesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository

    async def execute(self, actor: Actor, project_key: str, case_filter: TestCaseFilter) -> list[TestCaseSummary]:
        query = None if case_filter.query is None else case_filter.query.strip() or None
        story_key = None if case_filter.story_key is None else case_filter.story_key.strip().upper()
        normalized_filter = case_filter.model_copy(update={"query": query, "story_key": story_key})
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_VIEW)
            return await self._test_case_repository.list_summaries(access.project_id, normalized_filter)
