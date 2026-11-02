from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.integrations.typing.constants.webhook import MAX_WEBHOOK_DESCRIPTION_LENGTH, MAX_WEBHOOK_URL_LENGTH
from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.shared.common import WireModel

WebhookUrl = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_WEBHOOK_URL_LENGTH)]
WebhookDescription = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_WEBHOOK_DESCRIPTION_LENGTH)
]
WebhookEvents = Annotated[list[IntegrationEvent], Field(min_length=1, max_length=len(IntegrationEvent))]


class CreateWebhookRequest(WireModel):
    url: WebhookUrl
    description: WebhookDescription | None = None
    events: WebhookEvents
    is_active: bool = True
