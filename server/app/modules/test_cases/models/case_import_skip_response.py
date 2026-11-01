from app.modules.test_cases.typing.enums import CaseImportSkipReason
from app.shared.common import WireModel


class CaseImportSkipResponse(WireModel):
    location: str
    reason: CaseImportSkipReason
