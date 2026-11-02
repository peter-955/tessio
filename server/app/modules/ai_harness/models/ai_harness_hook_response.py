from app.shared.common import WireModel


class AiHarnessHookResponse(WireModel):
    event: str
    tool_name: str | None
    script: str
    timeout_seconds: int | None
