from datetime import UTC, datetime
from uuid import uuid7

from app.modules.suites.domains.suite_detail.entity import SuiteDetail
from app.modules.suites.domains.test_suite.entity import TestSuite
from app.modules.suites.domains.test_suite.repository import TestSuiteRepository
from app.modules.suites.errors import SuiteNameAlreadyUsedError
from app.modules.suites.utils.suite_event import build_suite_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CreateSuiteUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_suite_repository: TestSuiteRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_suite_repository = test_suite_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, name: str, description: str | None) -> SuiteDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.SUITE_EDIT)
            if await self._test_suite_repository.find_active_by_name(access.project_id, name) is not None:
                raise SuiteNameAlreadyUsedError
            suite = TestSuite(
                id=uuid7(),
                project_id=access.project_id,
                name=name,
                description=description or None,
                archived_at=None,
                created_by=actor.user_id,
                created_at=datetime.now(UTC),
            )
            await self._test_suite_repository.add(suite)
        await self._live_event_publisher.publish(build_suite_changed_event(suite))
        return SuiteDetail(suite=suite, cases=[], last_run=None, running_run=None)
