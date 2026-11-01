from uuid import UUID

from app.modules.story_context.domains.context_file.entity import ContextFile
from app.modules.test_cases import TestCasePriority, TestStep
from app.shared.common import Entity


class ContextCase(Entity):
    id: UUID
    code: str
    title: str
    priority: TestCasePriority
    version_number: int
    business_value: str | None
    preconditions: str | None
    steps: list[TestStep]
    criterion_ids: list[UUID]
    data_keys: list[str]
    files: list[ContextFile]
