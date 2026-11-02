from uuid import UUID

from pydantic import Field

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
    labels: list[str]
    parameters: list[str] = Field(default_factory=list)
    data_rows: list[dict[str, str]] = Field(default_factory=list)
