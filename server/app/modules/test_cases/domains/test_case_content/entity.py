from uuid import UUID

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
