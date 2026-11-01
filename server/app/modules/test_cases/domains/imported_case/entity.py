from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.typing.enums import TestCasePriority
from app.shared.common import Entity


class ImportedCase(Entity):
    location: str
    story_key: str | None
    title: str
    priority: TestCasePriority
    business_value: str | None
    preconditions: str | None
    steps: list[TestStep]
    criterion_codes: list[str]
