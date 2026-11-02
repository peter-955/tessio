from uuid import UUID

from pydantic import Field

from app.modules.suites.typing.constants.suite import MAX_SUITE_CASES
from app.shared.common import WireModel


class SetSuiteCasesRequest(WireModel):
    test_case_ids: list[UUID] = Field(max_length=MAX_SUITE_CASES)
