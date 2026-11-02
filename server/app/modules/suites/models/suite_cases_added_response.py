from app.modules.suites.models.suite_detail_response import SuiteDetailResponse
from app.shared.common import WireModel


class SuiteCasesAddedResponse(WireModel):
    added_count: int
    suite: SuiteDetailResponse
