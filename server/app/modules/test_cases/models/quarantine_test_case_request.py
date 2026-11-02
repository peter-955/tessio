from typing import Annotated

from pydantic import StringConstraints

from app.modules.test_cases.typing.constants.flaky_case import MAX_QUARANTINE_REASON_LENGTH
from app.shared.common import WireModel


class QuarantineTestCaseRequest(WireModel):
    reason: Annotated[str, StringConstraints(strip_whitespace=True, max_length=MAX_QUARANTINE_REASON_LENGTH)] | None = (
        None
    )
