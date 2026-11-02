from app.modules.integrations.models.webhook_response import WebhookResponse
from app.shared.common import WireModel


class WebhookWithSecretResponse(WireModel):
    webhook: WebhookResponse
    secret: str | None
