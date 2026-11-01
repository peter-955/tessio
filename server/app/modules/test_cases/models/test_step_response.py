from app.shared.common import WireModel


class TestStepResponse(WireModel):
    order: int
    action: str
    expected: str | None
