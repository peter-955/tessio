from app.modules.runs.typing.enums import ResultStatus, UnmappedTestReason
from app.shared.common import WireModel


class UnmappedTestResponse(WireModel):
    name: str
    classname: str | None
    status: ResultStatus
    reason: UnmappedTestReason
