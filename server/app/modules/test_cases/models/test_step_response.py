from app.shared.common import WireModel


class TestStepResponse(WireModel):
    order: int
    action: str | None
    expected: str | None
    shared_step_key: str | None
