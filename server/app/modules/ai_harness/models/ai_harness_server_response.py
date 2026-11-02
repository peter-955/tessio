from app.shared.common import WireModel


class AiHarnessServerResponse(WireModel):
    version: str
    build_commit: str | None
