from app.modules.insights.domains.case_latest_result.entity import CaseLatestResult
from app.modules.insights.ports.coverage_reader import CoverageReader
from app.modules.insights.ports.story_scope_reader import StoryScopeReader
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListCaseLatestResultsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        story_scope_reader: StoryScopeReader,
        coverage_reader: CoverageReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._story_scope_reader = story_scope_reader
        self._coverage_reader = coverage_reader

    async def execute(self, actor: Actor, project_key: str, story_key: str | None) -> list[CaseLatestResult]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            if story_key is None:
                cases = await self._coverage_reader.list_cases(access.project_id, None, True)
            else:
                story = await self._story_scope_reader.find_story(access.project_id, story_key)
                if story is None:
                    return []
                cases = await self._coverage_reader.list_cases(access.project_id, [story.id], True)
        return [
            CaseLatestResult(case_id=case.id, code=case.code, story_id=case.story_id, latest_result=case.latest_result)
            for case in cases
        ]
