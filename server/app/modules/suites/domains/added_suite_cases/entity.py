from app.modules.suites.domains.suite_detail.entity import SuiteDetail
from app.shared.common import Entity


class AddedSuiteCases(Entity):
    added_count: int
    detail: SuiteDetail
