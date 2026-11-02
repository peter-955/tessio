from datetime import UTC, datetime
from uuid import UUID

from app.modules.runs import SuiteNotFoundError
from app.modules.suites.domains.suite_detail.entity import SuiteDetail
from app.modules.suites.domains.test_suite.repository import TestSuiteRepository
from app.modules.suites.ports.suite_view_reader import SuiteViewReader
from app.modules.suites.utils.suite_detail import load_suite_detail
from app.modules.suites.utils.suite_event import build_suite_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ArchiveSuiteUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_suite_repository: TestSuiteRepository,
        suite_view_reader: SuiteViewReader,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_suite_repository = test_suite_repository
        self._suite_view_reader = suite_view_reader
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, suite_id: UUID) -> SuiteDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.SUITE_EDIT)
            suite = await self._test_suite_repository.find_by_id_for_update(access.project_id, suite_id)
            if suite is None:
                raise SuiteNotFoundError
            is_archiving = not suite.is_archived
            if is_archiving:
                suite = suite.model_copy(update={"archived_at": datetime.now(UTC)})
                await self._test_suite_repository.save(suite)
            detail = await load_suite_detail(self._suite_view_reader, suite)
        if is_archiving:
            await self._live_event_publisher.publish(build_suite_changed_event(suite))
        return detail
