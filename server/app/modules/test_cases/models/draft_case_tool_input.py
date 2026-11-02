from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.test_cases.models.draft_step_tool_input import DraftStepToolInput
from app.modules.test_cases.typing.constants import (
    MAX_CRITERION_LINKS,
    MAX_DRAFT_CASE_SOURCE_LENGTH,
    MAX_STORY_KEY_LENGTH,
)
from app.modules.test_cases.typing.enums import TestCasePriority
from app.shared.common import ToolModel


class DraftCaseToolInput(ToolModel):
    story_key: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_STORY_KEY_LENGTH)]
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    priority: TestCasePriority = TestCasePriority.MEDIUM
    business_value: Annotated[str, StringConstraints(strip_whitespace=True)] | None = None
    preconditions: Annotated[str, StringConstraints(strip_whitespace=True)] | None = None
    steps: Annotated[list[DraftStepToolInput], Field(min_length=1)]
    criterion_codes: list[str] = Field(default_factory=list, max_length=MAX_CRITERION_LINKS)
    source: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_DRAFT_CASE_SOURCE_LENGTH)
    ]
