from app.modules.integrations.models.create_webhook_request import WebhookDescription, WebhookEvents, WebhookUrl
from app.shared.common import WireModel


class UpdateWebhookRequest(WireModel):
    url: WebhookUrl | None = None
    description: WebhookDescription | None = None
    events: WebhookEvents | None = None
    is_active: bool | None = None
    rotate_secret: bool = False
