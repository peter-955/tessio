from pydantic import Field

from app.modules.failures.typing.constants.failure import MAX_CAUSE_REASON_LENGTH
from app.modules.runs import SuspectedCause
from app.shared.common import WireModel


class ChangeFailureCauseRequest(WireModel):
    cause: SuspectedCause
    reason: str | None = Field(default=None, max_length=MAX_CAUSE_REASON_LENGTH)
