from uuid import UUID

from app.shared.common import Entity


class MissingScreenshot(Entity):
    case_result_id: UUID
    test_case_id: UUID
    code: str
    step_order: int
    iteration: int | None = None
