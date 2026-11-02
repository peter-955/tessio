from app.modules.runs.domains.import_case.entity import ImportCase
from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import Entity


class ImportedCaseOutcome(Entity):
    case: ImportCase
    status: ResultStatus
    error: str | None
    duration_ms: int | None
