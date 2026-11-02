from uuid import UUID

from pydantic import Field

from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.typing.enums import TestCasePriority
from app.shared.common import Entity


class TestCaseContent(Entity):
    title: str
    priority: TestCasePriority
    business_value: str | None
    preconditions: str | None
    steps: list[TestStep]
    criterion_ids: list[UUID]
    parameters: list[str] = Field(default_factory=list)
    data_rows: list[dict[str, str]] = Field(default_factory=list)
