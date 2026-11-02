from datetime import UTC, datetime
from uuid import UUID

from app.modules.suites.domains.suite_case.repository import SuiteCaseRepository
from app.modules.suites.domains.suite_detail.entity import SuiteDetail
from app.modules.suites.domains.test_suite.repository import TestSuiteRepository
from app.modules.suites.errors import DuplicateSuiteCaseError, TooManySuiteCasesError, UnknownSuiteCasesError
from app.modules.suites.ports.suite_view_reader import SuiteViewReader
from app.modules.suites.typing.constants.suite import MAX_SUITE_CASES
from app.modules.suites.utils.suite_detail import load_suite_detail, lock_editable_suite
from app.modules.suites.utils.suite_event import build_suite_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class SetSuiteCasesUseCase:
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

    async def execute(self, actor: Actor, project_key: str, suite_id: UUID, test_case_ids: list[UUID]) -> SuiteDetail:
        if len(set(test_case_ids)) != len(test_case_ids):
            raise DuplicateSuiteCaseError
        if len(test_case_ids) > MAX_SUITE_CASES:
            raise TooManySuiteCasesError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.SUITE_EDIT)
            suite = await lock_editable_suite(self._test_suite_repository, access.project_id, suite_id)
            known_ids = await self._suite_view_reader.list_project_case_ids(access.project_id, test_case_ids)
            if len(known_ids) != len(test_case_ids):
                raise UnknownSuiteCasesError
            is_changing = await self._suite_case_repository.list_case_ids(suite.id) != test_case_ids
            if is_changing:
                await self._suite_case_repository.replace(suite.id, test_case_ids, datetime.now(UTC))
            detail = await load_suite_detail(self._suite_view_reader, suite)
        if is_changing:
            await self._live_event_publisher.publish(build_suite_changed_event(suite))
        return detail
