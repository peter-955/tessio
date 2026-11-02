from uuid import UUID

from app.modules.runs import SuiteArchivedError, SuiteNotFoundError
from app.modules.suites.domains.suite_detail.entity import SuiteDetail
from app.modules.suites.domains.test_suite.entity import TestSuite
from app.modules.suites.domains.test_suite.repository import TestSuiteRepository
from app.modules.suites.ports.suite_view_reader import SuiteViewReader


async def load_suite_detail(suite_view_reader: SuiteViewReader, suite: TestSuite) -> SuiteDetail:
    return SuiteDetail(
        suite=suite,
        cases=await suite_view_reader.list_case_views(suite.id),
        last_run=await suite_view_reader.find_last_run(suite.id),
        running_run=await suite_view_reader.find_running_run(suite.id),
    )


async def lock_editable_suite(repository: TestSuiteRepository, project_id: UUID, suite_id: UUID) -> TestSuite:
    suite = await repository.find_by_id_for_update(project_id, suite_id)
    if suite is None:
        raise SuiteNotFoundError
    if suite.is_archived:
        raise SuiteArchivedError
    return suite
