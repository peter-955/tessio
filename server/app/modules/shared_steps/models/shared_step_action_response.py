from app.shared.common import WireModel


class SharedStepActionResponse(WireModel):
    order: int
    action: str
    expected: str | None
