from app.modules.integrations.domains.webhook_summary.entity import WebhookSummary
from app.shared.common import Entity


class CreatedWebhook(Entity):
    summary: WebhookSummary
    secret: str | None
