from fastapi import Request

from app.modules.integrations.usecases.create_webhook import CreateWebhookUseCase
from app.modules.integrations.usecases.delete_webhook import DeleteWebhookUseCase
from app.modules.integrations.usecases.list_webhook_deliveries import ListWebhookDeliveriesUseCase
from app.modules.integrations.usecases.list_webhooks import ListWebhooksUseCase
from app.modules.integrations.usecases.redeliver_webhook import RedeliverWebhookUseCase
from app.modules.integrations.usecases.update_webhook import UpdateWebhookUseCase


def get_list_webhooks(request: Request) -> ListWebhooksUseCase:
    use_case: ListWebhooksUseCase = request.app.state.container.list_webhooks
    return use_case


def get_create_webhook(request: Request) -> CreateWebhookUseCase:
    use_case: CreateWebhookUseCase = request.app.state.container.create_webhook
    return use_case


def get_update_webhook(request: Request) -> UpdateWebhookUseCase:
    use_case: UpdateWebhookUseCase = request.app.state.container.update_webhook
    return use_case


def get_delete_webhook(request: Request) -> DeleteWebhookUseCase:
    use_case: DeleteWebhookUseCase = request.app.state.container.delete_webhook
    return use_case


def get_list_webhook_deliveries(request: Request) -> ListWebhookDeliveriesUseCase:
    use_case: ListWebhookDeliveriesUseCase = request.app.state.container.list_webhook_deliveries
    return use_case


def get_redeliver_webhook(request: Request) -> RedeliverWebhookUseCase:
    use_case: RedeliverWebhookUseCase = request.app.state.container.redeliver_webhook
    return use_case
