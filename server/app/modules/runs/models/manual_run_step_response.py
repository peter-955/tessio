from app.shared.common import WireModel


class ManualRunStepResponse(WireModel):
    order: int
    action: str
    expected: str | None
