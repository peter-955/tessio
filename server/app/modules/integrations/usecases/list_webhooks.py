from app.modules.integrations.domains.webhook.repository import WebhookRepository
from app.modules.integrations.domains.webhook_delivery.repository import WebhookDeliveryRepository
from app.modules.integrations.domains.webhook_summary.entity import WebhookSummary
from app.modules.integrations.utils.webhook_summary import build_webhook_summary
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListWebhooksUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        webhook_repository: WebhookRepository,
        webhook_delivery_repository: WebhookDeliveryRepository,
        secret_cipher: SecretCipher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._webhook_repository = webhook_repository
        self._webhook_delivery_repository = webhook_delivery_repository
        self._secret_cipher = secret_cipher

    async def execute(self, actor: Actor, project_key: str) -> list[WebhookSummary]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.INTEGRATION_MANAGE)
            webhooks = await self._webhook_repository.list_for_project(access.project_id)
            latest = await self._webhook_delivery_repository.map_latest([webhook.id for webhook in webhooks])
        return [build_webhook_summary(webhook, self._secret_cipher, latest.get(webhook.id)) for webhook in webhooks]
