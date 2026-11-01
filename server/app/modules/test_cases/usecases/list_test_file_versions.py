from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.domains.test_file_version.repository import TestFileVersionRepository
from app.modules.test_cases.domains.test_file_version_detail.entity import TestFileVersionDetail
from app.modules.test_cases.errors import TestFileNotFoundError
from app.modules.test_cases.utils.test_case_lookup import require_test_case
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListTestFileVersionsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        test_file_repository: TestFileRepository,
        test_file_version_repository: TestFileVersionRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._test_file_repository = test_file_repository
        self._test_file_version_repository = test_file_version_repository

    async def execute(
        self, actor: Actor, project_key: str, case_code: str, file_key: str
    ) -> list[TestFileVersionDetail]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_VIEW)
            test_case = await require_test_case(self._test_case_repository, access.project_id, case_code)
            test_file = await self._test_file_repository.find_by_key(test_case.id, file_key)
            if test_file is None:
                raise TestFileNotFoundError
            return await self._test_file_version_repository.list_for_file(test_file.id)
