from app.modules.integrations.domains.webhook.entity import Webhook
from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.modules.integrations.domains.webhook_summary.entity import WebhookSummary
from app.modules.integrations.utils.webhook_secret import build_webhook_secret_hint
from app.shared.crypto import SecretCipher


def build_webhook_summary(
    webhook: Webhook, secret_cipher: SecretCipher, last_delivery: WebhookDelivery | None
) -> WebhookSummary:
    secret = secret_cipher.decrypt(webhook.secret_encrypted).decode()
    return WebhookSummary(webhook=webhook, secret_hint=build_webhook_secret_hint(secret), last_delivery=last_delivery)
