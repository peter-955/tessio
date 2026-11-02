from app.shared.common import Entity


class FailedRequest(Entity):
    method: str
    path: str
    status: int
    excerpt: str | None
