from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import Entity


class JunitTest(Entity):
    name: str
    classname: str | None
    status: ResultStatus
    message: str | None
    duration_ms: int | None
    case_numbers: list[int]
