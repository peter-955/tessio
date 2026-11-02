from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints

from app.modules.suites.typing.constants.suite import MAX_FILTER_LABELS
from app.modules.test_cases import TestCasePriority
from app.shared.common import WireModel

LabelName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class AddSuiteCasesByFilterRequest(WireModel):
    labels: list[LabelName] = Field(default_factory=list, max_length=MAX_FILTER_LABELS)
    priorities: list[TestCasePriority] = Field(default_factory=list, max_length=len(TestCasePriority))
    story_key: Annotated[str, StringConstraints(strip_whitespace=True, max_length=64)] | None = None
    sprint_id: UUID | None = None
