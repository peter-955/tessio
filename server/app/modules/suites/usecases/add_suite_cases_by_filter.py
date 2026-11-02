from datetime import UTC, datetime
from uuid import UUID

from app.modules.suites.domains.added_suite_cases.entity import AddedSuiteCases
from app.modules.suites.domains.suite_case.repository import SuiteCaseRepository
from app.modules.suites.domains.suite_case_filter.entity import SuiteCaseFilter
from app.modules.suites.domains.test_suite.repository import TestSuiteRepository
from app.modules.suites.errors import (
    SuiteFilterRequiredError,
    TooManySuiteCasesError,
    UnknownFilterSprintError,
    UnknownFilterStoryError,
)
from app.modules.suites.ports.suite_view_reader import SuiteViewReader
from app.modules.suites.typing.constants.suite import MAX_SUITE_CASES
from app.modules.suites.utils.suite_detail import load_suite_detail, lock_editable_suite
from app.modules.suites.utils.suite_event import build_suite_changed_event
from app.modules.test_cases import TestCasePriority
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class AddSuiteCasesByFilterUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_suite_repository: TestSuiteRepository,
        suite_case_repository: SuiteCaseRepository,
        suite_view_reader: SuiteViewReader,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_suite_repository = test_suite_repository
        self._suite_case_repository = suite_case_repository
        self._suite_view_reader = suite_view_reader
        self._live_event_publisher = live_event_publisher

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        suite_id: UUID,
        label_names: list[str],
        priorities: list[TestCasePriority],
        story_key: str | None,
        sprint_id: UUID | None,
    ) -> AddedSuiteCases:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.SUITE_EDIT)
            suite = await lock_editable_suite(self._test_suite_repository, access.project_id, suite_id)
            case_filter = SuiteCaseFilter(
                label_names=list(dict.fromkeys(name.strip() for name in label_names if name.strip())),
                priorities=list(dict.fromkeys(priorities)),
                story_id=await self._find_story_id(access.project_id, story_key),
                sprint_id=sprint_id,
            )
            if case_filter.is_empty:
                raise SuiteFilterRequiredError
            if sprint_id is not None and not await self._suite_view_reader.has_sprint(access.project_id, sprint_id):
                raise UnknownFilterSprintError
            current_ids = await self._suite_case_repository.list_case_ids(suite.id)
            known_ids = set(current_ids)
            added_ids = [
                case_id
                for case_id in await self._suite_view_reader.list_matching_case_ids(access.project_id, case_filter)
                if case_id not in known_ids
            ]
            if len(current_ids) + len(added_ids) > MAX_SUITE_CASES:
                raise TooManySuiteCasesError
            if added_ids:
                await self._suite_case_repository.replace(suite.id, [*current_ids, *added_ids], datetime.now(UTC))
            detail = await load_suite_detail(self._suite_view_reader, suite)
        if added_ids:
            await self._live_event_publisher.publish(build_suite_changed_event(suite))
        return AddedSuiteCases(added_count=len(added_ids), detail=detail)

    async def _find_story_id(self, project_id: UUID, story_key: str | None) -> UUID | None:
        if story_key is None or not story_key.strip():
            return None
        story_id = await self._suite_view_reader.find_story_id(project_id, story_key)
        if story_id is None:
            raise UnknownFilterStoryError(story_key.strip().upper())
        return story_id
