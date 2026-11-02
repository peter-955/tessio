from collections.abc import Sequence

from app.modules.test_cases.domains.case_import_preview_item.entity import CaseImportPreviewItem
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.utils.case_import_plan import load_case_import_plan
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class CheckDraftCasesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        story_reader: StoryReader,
        criterion_reader: CriterionReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._story_reader = story_reader
        self._criterion_reader = criterion_reader

    async def execute_in_token_project(
        self, actor: Actor, cases: Sequence[ImportedCase]
    ) -> list[CaseImportPreviewItem]:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.TEST_CASE_EDIT)
            plan = await load_case_import_plan(
                cases, access.project_id, self._test_case_repository, self._story_reader, self._criterion_reader
            )
        return plan.items
