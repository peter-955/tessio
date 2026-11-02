from uuid import UUID

from app.modules.integrations.domains.created_webhook.entity import CreatedWebhook
from app.modules.integrations.domains.webhook.repository import WebhookRepository
from app.modules.integrations.domains.webhook_changes.entity import WebhookChanges
from app.modules.integrations.domains.webhook_delivery.repository import WebhookDeliveryRepository
from app.modules.integrations.errors import WebhookNotFoundError, WebhookUrlInvalidError
from app.modules.integrations.utils.webhook_event import build_webhook_changed_event
from app.modules.integrations.utils.webhook_events import normalize_webhook_events
from app.modules.integrations.utils.webhook_secret import generate_webhook_secret
from app.modules.integrations.utils.webhook_summary import build_webhook_summary
from app.modules.integrations.utils.webhook_url import is_allowed_webhook_url
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UpdateWebhookUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        webhook_repository: WebhookRepository,
        webhook_delivery_repository: WebhookDeliveryRepository,
        secret_cipher: SecretCipher,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._webhook_repository = webhook_repository
        self._webhook_delivery_repository = webhook_delivery_repository
        self._secret_cipher = secret_cipher
        self._live_event_publisher = live_event_publisher

    async def execute(
        self, actor: Actor, project_key: str, webhook_id: UUID, changes: WebhookChanges
    ) -> CreatedWebhook:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            webhook = await self._webhook_repository.find(access.project_id, webhook_id)
            if webhook is None:
                raise WebhookNotFoundError
            if changes.url is not None and not is_allowed_webhook_url(changes.url):
                raise WebhookUrlInvalidError
            secret = generate_webhook_secret() if changes.is_rotating_secret else None
            update: dict[str, object] = {}
            if changes.url is not None:
                update["url"] = changes.url
            if changes.description is not None or changes.is_clearing_description:
                update["description"] = changes.description
            if changes.events is not None:
                update["events"] = normalize_webhook_events(changes.events)
            if changes.is_active is not None:
                update["is_active"] = changes.is_active
            if secret is not None:
                update["secret_encrypted"] = self._secret_cipher.encrypt(secret.encode())
            updated = webhook.model_copy(update=update)
            await self._webhook_repository.save(updated)
            latest = await self._webhook_delivery_repository.map_latest([updated.id])
        await self._live_event_publisher.publish(build_webhook_changed_event(updated.project_id, updated.id))
        return CreatedWebhook(
            summary=build_webhook_summary(updated, self._secret_cipher, latest.get(updated.id)), secret=secret
        )
