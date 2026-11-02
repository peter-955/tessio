from app.modules.runs.typing.enums import ResultStatus, UnmappedTestReason
from app.shared.common import Entity


class UnmappedTest(Entity):
    name: str
    classname: str | None
    status: ResultStatus
    reason: UnmappedTestReason
