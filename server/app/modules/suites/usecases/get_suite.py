from uuid import UUID

from app.modules.runs import SuiteNotFoundError
from app.modules.suites.domains.suite_detail.entity import SuiteDetail
from app.modules.suites.domains.test_suite.repository import TestSuiteRepository
from app.modules.suites.ports.suite_view_reader import SuiteViewReader
from app.modules.suites.utils.suite_detail import load_suite_detail
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetSuiteUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_suite_repository: TestSuiteRepository,
        suite_view_reader: SuiteViewReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_suite_repository = test_suite_repository
        self._suite_view_reader = suite_view_reader

    async def execute(self, actor: Actor, project_key: str, suite_id: UUID) -> SuiteDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_VIEW)
            suite = await self._test_suite_repository.find_by_id(access.project_id, suite_id)
            if suite is None:
                raise SuiteNotFoundError
            detail = await load_suite_detail(self._suite_view_reader, suite)
        return detail
