from app.shared.common import WireModel


class ExecutorCountResponse(WireModel):
    executor: str
    count: int
