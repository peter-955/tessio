from uuid import UUID

from app.modules.test_cases.domains.case_import_preview.entity import CaseImportPreview
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.utils.case_import_loader import load_case_import
from app.modules.test_cases.utils.case_import_plan import load_case_import_plan
from app.modules.test_data import ImportFileReader
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class PreviewTestCaseImportUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        story_reader: StoryReader,
        criterion_reader: CriterionReader,
        import_file_reader: ImportFileReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._story_reader = story_reader
        self._criterion_reader = criterion_reader
        self._import_file_reader = import_file_reader

    async def execute(self, actor: Actor, project_key: str, file_id: UUID) -> CaseImportPreview:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            parsed_import = await load_case_import(self._import_file_reader, access.project_id, file_id, actor.user_id)
            plan = await load_case_import_plan(
                parsed_import.cases,
                access.project_id,
                self._test_case_repository,
                self._story_reader,
                self._criterion_reader,
            )
        return CaseImportPreview(format=parsed_import.format, items=plan.items, skipped=parsed_import.skipped)
