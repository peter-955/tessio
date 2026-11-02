from app.modules.integrations.domains.created_webhook.entity import CreatedWebhook
from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.modules.integrations.domains.webhook_summary.entity import WebhookSummary
from app.modules.integrations.models.webhook_delivery_response import WebhookDeliveryResponse
from app.modules.integrations.models.webhook_response import WebhookResponse
from app.modules.integrations.models.webhook_with_secret_response import WebhookWithSecretResponse


def build_webhook_response(summary: WebhookSummary) -> WebhookResponse:
    webhook = summary.webhook
    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        description=webhook.description,
        events=webhook.events,
        is_active=webhook.is_active,
        secret_hint=summary.secret_hint,
        created_at=webhook.created_at,
        last_delivery=None if summary.last_delivery is None else build_webhook_delivery_response(summary.last_delivery),
    )


def build_webhook_with_secret_response(created: CreatedWebhook) -> WebhookWithSecretResponse:
    return WebhookWithSecretResponse(webhook=build_webhook_response(created.summary), secret=created.secret)


def build_webhook_delivery_response(delivery: WebhookDelivery) -> WebhookDeliveryResponse:
    return WebhookDeliveryResponse(
        id=delivery.id,
        webhook_id=delivery.webhook_id,
        event=delivery.event,
        status=delivery.status,
        attempts=delivery.attempts,
        response_status=delivery.response_status,
        error=delivery.error,
        redelivery_of_id=delivery.redelivery_of_id,
        last_attempt_at=delivery.last_attempt_at,
        delivered_at=delivery.delivered_at,
        created_at=delivery.created_at,
        payload=delivery.payload,
    )
