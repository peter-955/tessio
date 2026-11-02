from uuid import UUID

from app.modules.test_cases import TestStep
from app.shared.common import Entity


class GapCase(Entity):
    id: UUID
    code: str
    title: str
    version_number: int | None
    preconditions: str | None
    steps: list[TestStep]
