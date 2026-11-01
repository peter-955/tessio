from app.modules.test_cases.typing.enums import CaseImportProblem, TestCasePriority
from app.shared.common import Entity


class CaseImportPreviewItem(Entity):
    index: int
    location: str
    story_key: str | None
    title: str
    priority: TestCasePriority
    step_count: int
    criterion_codes: list[str]
    unknown_criterion_codes: list[str]
    is_duplicate: bool
    problem: CaseImportProblem | None
