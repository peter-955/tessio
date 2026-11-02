from uuid import UUID

from app.modules.suites.domains.suite_detail.entity import SuiteDetail
from app.modules.suites.domains.suite_patch.entity import SuitePatch
from app.modules.suites.domains.test_suite.repository import TestSuiteRepository
from app.modules.suites.errors import SuiteNameAlreadyUsedError
from app.modules.suites.ports.suite_view_reader import SuiteViewReader
from app.modules.suites.utils.suite_detail import load_suite_detail, lock_editable_suite
from app.modules.suites.utils.suite_event import build_suite_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UpdateSuiteUseCase:
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

    async def execute(self, actor: Actor, project_key: str, suite_id: UUID, patch: SuitePatch) -> SuiteDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.SUITE_EDIT)
            suite = await lock_editable_suite(self._test_suite_repository, access.project_id, suite_id)
            changes: dict[str, object] = {}
            if patch.name is not None and patch.name != suite.name:
                same_name = await self._test_suite_repository.find_active_by_name(access.project_id, patch.name)
                if same_name is not None and same_name.id != suite.id:
                    raise SuiteNameAlreadyUsedError
                changes["name"] = patch.name
            if patch.is_changing_description:
                changes["description"] = patch.description or None
            updated = suite.model_copy(update=changes)
            if changes:
                await self._test_suite_repository.save(updated)
            detail = await load_suite_detail(self._suite_view_reader, updated)
        if changes:
            await self._live_event_publisher.publish(build_suite_changed_event(updated))
        return detail
