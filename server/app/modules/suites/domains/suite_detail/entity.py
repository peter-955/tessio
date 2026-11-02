from app.modules.suites.domains.suite_case_view.entity import SuiteCaseView
from app.modules.suites.domains.suite_run_reference.entity import SuiteRunReference
from app.modules.suites.domains.test_suite.entity import TestSuite
from app.shared.common import Entity


class SuiteDetail(Entity):
    suite: TestSuite
    cases: list[SuiteCaseView]
    last_run: SuiteRunReference | None
    running_run: SuiteRunReference | None
