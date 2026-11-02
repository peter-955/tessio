from app.shared.common import WireModel


class FailedRequestResponse(WireModel):
    method: str
    path: str
    status: int
    excerpt: str | None
