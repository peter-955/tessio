from app.modules.test_cases.typing.enums import CaseImportSkipReason
from app.shared.common import Entity


class CaseImportSkip(Entity):
    location: str
    reason: CaseImportSkipReason
