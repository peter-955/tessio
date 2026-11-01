from uuid import UUID

from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.errors import TestCaseNotFoundError
from app.modules.test_cases.utils.case_code import parse_case_code


async def require_test_case(repository: TestCaseRepository, project_id: UUID, case_code: str) -> TestCase:
    test_case = await repository.find_by_number(project_id, parse_case_code(case_code))
    if test_case is None:
        raise TestCaseNotFoundError
    return test_case


async def require_locked_test_case(repository: TestCaseRepository, project_id: UUID, case_code: str) -> TestCase:
    test_case = await repository.find_by_number_for_update(project_id, parse_case_code(case_code))
    if test_case is None:
        raise TestCaseNotFoundError
    return test_case


async def require_current_version(repository: TestCaseVersionRepository, test_case: TestCase) -> TestCaseVersion:
    version = await repository.find_by_id(test_case.current_version_id)
    if version is None:
        raise TestCaseNotFoundError
    return version
