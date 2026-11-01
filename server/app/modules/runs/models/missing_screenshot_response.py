from uuid import UUID

from app.shared.common import WireModel


class MissingScreenshotResponse(WireModel):
    case_result_id: UUID
    test_case_id: UUID
    code: str
    step_order: int
