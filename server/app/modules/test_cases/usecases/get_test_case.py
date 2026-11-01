from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_detail.entity import TestCaseDetail
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.modules.test_cases.ports.data_key_reader import DataKeyReader
from app.modules.test_cases.ports.story_reader import StoryReader
from app.modules.test_cases.utils.test_case_detail import load_test_case_detail
from app.modules.test_cases.utils.test_case_lookup import require_test_case
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetTestCaseUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_case_repository: TestCaseRepository,
        test_case_version_repository: TestCaseVersionRepository,
        test_file_repository: TestFileRepository,
        story_reader: StoryReader,
        criterion_reader: CriterionReader,
        data_key_reader: DataKeyReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_case_repository = test_case_repository
        self._test_case_version_repository = test_case_version_repository
        self._test_file_repository = test_file_repository
        self._story_reader = story_reader
        self._criterion_reader = criterion_reader
        self._data_key_reader = data_key_reader

    async def execute(self, actor: Actor, project_key: str, case_code: str) -> TestCaseDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_VIEW)
            test_case = await require_test_case(self._test_case_repository, access.project_id, case_code)
            return await load_test_case_detail(
                test_case,
                self._test_case_version_repository,
                self._test_file_repository,
                self._story_reader,
                self._criterion_reader,
                self._data_key_reader,
            )
