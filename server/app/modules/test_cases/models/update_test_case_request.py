from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints

from app.modules.test_cases.models.test_step_request import TestStepRequest
from app.modules.test_cases.typing.constants import MAX_CRITERION_LINKS, MAX_STEPS, MAX_TEXT_LENGTH, MAX_TITLE_LENGTH
from app.modules.test_cases.typing.enums import TestCasePriority
from app.shared.common import WireModel


class UpdateTestCaseRequest(WireModel):
    base_version_number: int = Field(ge=1)
    title: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_TITLE_LENGTH)] | None
    ) = None
    priority: TestCasePriority | None = None
    business_value: str | None = Field(default=None, max_length=MAX_TEXT_LENGTH)
    preconditions: str | None = Field(default=None, max_length=MAX_TEXT_LENGTH)
    steps: list[TestStepRequest] | None = Field(default=None, max_length=MAX_STEPS)
    criterion_ids: list[UUID] | None = Field(default=None, max_length=MAX_CRITERION_LINKS)
