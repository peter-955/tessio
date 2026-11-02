from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.integrations.domains.webhook_changes.entity import WebhookChanges
from app.modules.integrations.models.create_webhook_request import CreateWebhookRequest
from app.modules.integrations.models.update_webhook_request import UpdateWebhookRequest
from app.modules.integrations.models.webhook_delivery_response import WebhookDeliveryResponse
from app.modules.integrations.models.webhook_response import WebhookResponse
from app.modules.integrations.models.webhook_with_secret_response import WebhookWithSecretResponse
from app.modules.integrations.typing.constants.webhook import (
    DEFAULT_WEBHOOK_DELIVERY_LIST_LIMIT,
    MAX_WEBHOOK_DELIVERY_LIST_LIMIT,
)
from app.modules.integrations.usecases.create_webhook import CreateWebhookUseCase
from app.modules.integrations.usecases.delete_webhook import DeleteWebhookUseCase
from app.modules.integrations.usecases.list_webhook_deliveries import ListWebhookDeliveriesUseCase
from app.modules.integrations.usecases.list_webhooks import ListWebhooksUseCase
from app.modules.integrations.usecases.redeliver_webhook import RedeliverWebhookUseCase
from app.modules.integrations.usecases.update_webhook import UpdateWebhookUseCase
from app.modules.integrations.utils.webhook_response import (
    build_webhook_delivery_response,
    build_webhook_response,
    build_webhook_with_secret_response,
)
from app.modules.integrations.webhook_dependencies import (
    get_create_webhook,
    get_delete_webhook,
    get_list_webhook_deliveries,
    get_list_webhooks,
    get_redeliver_webhook,
    get_update_webhook,
)
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

webhooks_router = APIRouter(prefix="/api", tags=["webhooks"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@webhooks_router.get("/projects/{project_key}/webhooks")
async def list_webhooks(
    project_key: str,
    actor: SignedInActor,
    use_case: Annotated[ListWebhooksUseCase, Depends(get_list_webhooks)],
) -> list[WebhookResponse]:
    return [build_webhook_response(summary) for summary in await use_case.execute(actor, project_key)]


@webhooks_router.post("/projects/{project_key}/webhooks", status_code=status.HTTP_201_CREATED)
async def create_webhook(
    project_key: str,
    body: CreateWebhookRequest,
    actor: SignedInActor,
    use_case: Annotated[CreateWebhookUseCase, Depends(get_create_webhook)],
) -> WebhookWithSecretResponse:
    created = await use_case.execute(actor, project_key, body.url, body.description, body.events, body.is_active)
    return build_webhook_with_secret_response(created)


@webhooks_router.patch("/projects/{project_key}/webhooks/{webhook_id}")
async def update_webhook(
    project_key: str,
    webhook_id: UUID,
    body: UpdateWebhookRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateWebhookUseCase, Depends(get_update_webhook)],
) -> WebhookWithSecretResponse:
    changes = WebhookChanges(
        url=body.url,
        description=body.description,
        is_clearing_description="description" in body.model_fields_set and body.description is None,
        events=body.events,
        is_active=body.is_active,
        is_rotating_secret=body.rotate_secret,
    )
    return build_webhook_with_secret_response(await use_case.execute(actor, project_key, webhook_id, changes))


@webhooks_router.delete("/projects/{project_key}/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    project_key: str,
    webhook_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[DeleteWebhookUseCase, Depends(get_delete_webhook)],
) -> None:
    await use_case.execute(actor, project_key, webhook_id)


@webhooks_router.get("/projects/{project_key}/webhooks/{webhook_id}/deliveries")
async def list_webhook_deliveries(
    project_key: str,
    webhook_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[ListWebhookDeliveriesUseCase, Depends(get_list_webhook_deliveries)],
    limit: Annotated[int, Query(ge=1, le=MAX_WEBHOOK_DELIVERY_LIST_LIMIT)] = DEFAULT_WEBHOOK_DELIVERY_LIST_LIMIT,
) -> list[WebhookDeliveryResponse]:
    deliveries = await use_case.execute(actor, project_key, webhook_id, limit)
    return [build_webhook_delivery_response(delivery) for delivery in deliveries]


@webhooks_router.post(
    "/projects/{project_key}/webhooks/{webhook_id}/redeliver/{delivery_id}", status_code=status.HTTP_202_ACCEPTED
)
async def redeliver_webhook(
    project_key: str,
    webhook_id: UUID,
    delivery_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[RedeliverWebhookUseCase, Depends(get_redeliver_webhook)],
) -> WebhookDeliveryResponse:
    return build_webhook_delivery_response(await use_case.execute(actor, project_key, webhook_id, delivery_id))
