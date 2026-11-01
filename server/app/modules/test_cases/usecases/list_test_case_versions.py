from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.utils.test_case_lookup import require_test_case
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListTestCaseVersionsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        test_case_version_repository: TestCaseVersionRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._test_case_version_repository = test_case_version_repository

    async def execute(self, actor: Actor, project_key: str, case_code: str) -> list[TestCaseVersion]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_VIEW)
            test_case = await require_test_case(self._test_case_repository, access.project_id, case_code)
            return await self._test_case_version_repository.list_for_case(test_case.id)
