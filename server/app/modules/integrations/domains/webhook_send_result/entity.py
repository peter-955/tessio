from app.shared.common import Entity


class WebhookSendResult(Entity):
    is_success: bool
    response_status: int | None
    error: str | None
