from uuid import UUID

from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.typing.enums import TestCasePriority
from app.shared.common import Entity


class TestCaseChanges(Entity):
    title: str | None = None
    priority: TestCasePriority | None = None
    business_value: str | None = None
    preconditions: str | None = None
    steps: list[TestStep] | None = None
    criterion_ids: list[UUID] | None = None
