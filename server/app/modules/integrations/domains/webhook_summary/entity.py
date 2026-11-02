from app.modules.integrations.domains.webhook.entity import Webhook
from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.shared.common import Entity


class WebhookSummary(Entity):
    webhook: Webhook
    secret_hint: str
    last_delivery: WebhookDelivery | None
