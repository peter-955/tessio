from datetime import UTC, datetime
from uuid import uuid7

from app.modules.integrations.domains.created_webhook.entity import CreatedWebhook
from app.modules.integrations.domains.webhook.entity import Webhook
from app.modules.integrations.domains.webhook.repository import WebhookRepository
from app.modules.integrations.errors import WebhookLimitReachedError, WebhookUrlInvalidError
from app.modules.integrations.typing.constants.webhook import MAX_WEBHOOKS_PER_PROJECT
from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.modules.integrations.utils.webhook_event import build_webhook_changed_event
from app.modules.integrations.utils.webhook_events import normalize_webhook_events
from app.modules.integrations.utils.webhook_secret import generate_webhook_secret
from app.modules.integrations.utils.webhook_summary import build_webhook_summary
from app.modules.integrations.utils.webhook_url import is_allowed_webhook_url
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CreateWebhookUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        webhook_repository: WebhookRepository,
        secret_cipher: SecretCipher,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._webhook_repository = webhook_repository
        self._secret_cipher = secret_cipher
        self._live_event_publisher = live_event_publisher

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        url: str,
        description: str | None,
        events: list[IntegrationEvent],
        is_active: bool,
    ) -> CreatedWebhook:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            if not is_allowed_webhook_url(url):
                raise WebhookUrlInvalidError
            if await self._webhook_repository.count_for_project(access.project_id) >= MAX_WEBHOOKS_PER_PROJECT:
                raise WebhookLimitReachedError(MAX_WEBHOOKS_PER_PROJECT)
            secret = generate_webhook_secret()
            webhook = Webhook(
                id=uuid7(),
                project_id=access.project_id,
                url=url,
                description=description,
                secret_encrypted=self._secret_cipher.encrypt(secret.encode()),
                events=normalize_webhook_events(events),
                is_active=is_active,
                created_by=actor.user_id,
                created_at=datetime.now(UTC),
            )
            await self._webhook_repository.save(webhook)
        await self._live_event_publisher.publish(build_webhook_changed_event(webhook.project_id, webhook.id))
        return CreatedWebhook(summary=build_webhook_summary(webhook, self._secret_cipher, None), secret=secret)
