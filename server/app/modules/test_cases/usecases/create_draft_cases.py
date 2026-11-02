from collections.abc import Sequence
from datetime import UTC, datetime

from app.modules.test_cases.domains.case_import_result.entity import CaseImportResult
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.domains.imported_case_code.entity import ImportedCaseCode
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_counter.repository import TestCaseCounterRepository
from app.modules.test_cases.errors import DraftCasesNotCreatableError
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.utils.case_import_plan import load_case_import_plan
from app.modules.test_cases.utils.imported_case_creation import create_imported_case
from app.modules.test_cases.utils.test_case_event import build_test_case_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class CreateDraftCasesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        story_reader: StoryReader,
        criterion_reader: CriterionReader,
        test_case_counter_repository: TestCaseCounterRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._story_reader = story_reader
        self._criterion_reader = criterion_reader
        self._test_case_counter_repository = test_case_counter_repository
        self._live_event_publisher = live_event_publisher

    async def execute_in_token_project(self, actor: Actor, cases: Sequence[ImportedCase]) -> CaseImportResult:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        now = datetime.now(UTC)
        created_cases: list[TestCase] = []
        created: list[ImportedCaseCode] = []
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.TEST_CASE_EDIT)
            plan = await load_case_import_plan(
                cases, access.project_id, self._test_case_repository, self._story_reader, self._criterion_reader
            )
            blocked_indexes = [item.index for item in plan.items if item.problem is not None]
            if blocked_indexes:
                raise DraftCasesNotCreatableError(blocked_indexes)
            for imported_case in cases:
                test_case = await create_imported_case(
                    imported_case,
                    plan,
                    access.project_id,
                    actor.user_id,
                    now,
                    self._test_case_repository,
                    self._test_case_counter_repository,
                )
                created_cases.append(test_case)
                created.append(
                    ImportedCaseCode(
                        code=test_case.code, story_key=imported_case.story_key or "", title=test_case.title
                    )
                )
        for test_case in created_cases:
            await self._live_event_publisher.publish(build_test_case_changed_event(test_case))
        return CaseImportResult(created=created)
