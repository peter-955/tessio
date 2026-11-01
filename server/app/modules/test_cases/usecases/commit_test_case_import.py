from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.test_cases.domains.case_import_plan.entity import CaseImportPlan
from app.modules.test_cases.domains.case_import_result.entity import CaseImportResult
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.domains.imported_case_code.entity import ImportedCaseCode
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_content.entity import TestCaseContent
from app.modules.test_cases.domains.test_case_counter.repository import TestCaseCounterRepository
from app.modules.test_cases.errors import CaseImportChoiceInvalidError
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.typing.enums import TestCaseStatus
from app.modules.test_cases.utils.case_import_loader import load_case_import
from app.modules.test_cases.utils.case_import_plan import load_case_import_plan
from app.modules.test_cases.utils.test_case_event import build_test_case_changed_event
from app.modules.test_cases.utils.test_case_version import build_test_case_version
from app.modules.test_data import ImportFileReader
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CommitTestCaseImportUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        story_reader: StoryReader,
        criterion_reader: CriterionReader,
        import_file_reader: ImportFileReader,
        test_case_counter_repository: TestCaseCounterRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._story_reader = story_reader
        self._criterion_reader = criterion_reader
        self._import_file_reader = import_file_reader
        self._test_case_counter_repository = test_case_counter_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, file_id: UUID, indexes: Sequence[int]) -> CaseImportResult:
        now = datetime.now(UTC)
        created_cases: list[TestCase] = []
        created: list[ImportedCaseCode] = []
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_EDIT)
            parsed_import = await load_case_import(self._import_file_reader, access.project_id, file_id, actor.user_id)
            plan = await load_case_import_plan(
                parsed_import, access.project_id, self._test_case_repository, self._story_reader, self._criterion_reader
            )
            chosen_indexes = list(dict.fromkeys(indexes))
            if any(index >= len(plan.items) or plan.items[index].problem is not None for index in chosen_indexes):
                raise CaseImportChoiceInvalidError
            for index in chosen_indexes:
                imported_case = parsed_import.cases[index]
                test_case = await self._create_case(imported_case, plan, access.project_id, actor.user_id, now)
                created_cases.append(test_case)
                created.append(
                    ImportedCaseCode(
                        code=test_case.code, story_key=imported_case.story_key or "", title=test_case.title
                    )
                )
        for test_case in created_cases:
            await self._live_event_publisher.publish(build_test_case_changed_event(test_case))
        return CaseImportResult(created=created)

    async def _create_case(
        self, imported_case: ImportedCase, plan: CaseImportPlan, project_id: UUID, created_by: UUID, now: datetime
    ) -> TestCase:
        story = plan.stories_by_key[imported_case.story_key or ""]
        criterion_ids_by_code = {
            criterion.code.upper(): criterion.id
            for criterion in plan.criteria_by_story_id.get(story.id, [])
            if not criterion.is_removed
        }
        criterion_ids = [
            criterion_ids_by_code[code.upper()]
            for code in imported_case.criterion_codes
            if code.upper() in criterion_ids_by_code
        ]
        content = TestCaseContent(
            title=imported_case.title,
            priority=imported_case.priority,
            business_value=imported_case.business_value,
            preconditions=imported_case.preconditions,
            steps=imported_case.steps,
            criterion_ids=list(dict.fromkeys(criterion_ids)),
        )
        number = await self._test_case_counter_repository.allocate_number(project_id, now)
        test_case_id = uuid7()
        version = build_test_case_version(test_case_id, 1, content, [], created_by, now)
        test_case = TestCase(
            id=test_case_id,
            project_id=project_id,
            story_id=story.id,
            number=number,
            title=version.title,
            priority=version.priority,
            status=TestCaseStatus.DRAFT,
            current_version_id=version.id,
            status_changed_at=None,
            status_changed_by=None,
            needs_review_at=None,
            needs_review_criterion_ids=[],
            reviewed_at=None,
            reviewed_by=None,
            created_by=created_by,
            created_at=now,
        )
        await self._test_case_repository.create(test_case, version)
        return test_case
