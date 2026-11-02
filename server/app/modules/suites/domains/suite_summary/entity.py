from app.modules.suites.domains.suite_run_reference.entity import SuiteRunReference
from app.modules.suites.domains.test_suite.entity import TestSuite
from app.shared.common import Entity


class SuiteSummary(Entity):
    suite: TestSuite
    case_count: int
    ready_case_count: int
    last_run: SuiteRunReference | None
