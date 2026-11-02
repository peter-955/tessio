from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.integrations.typing.constants.chat_channel import (
    MAX_CHAT_CHANNEL_NAME_LENGTH,
    MAX_CHAT_WEBHOOK_URL_LENGTH,
)
from app.modules.integrations.typing.enums.integration_event import IntegrationEvent

ChatChannelName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_CHAT_CHANNEL_NAME_LENGTH)
]
ChatWebhookUrl = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_CHAT_WEBHOOK_URL_LENGTH)
]
ChatChannelEvents = Annotated[list[IntegrationEvent], Field(min_length=1, max_length=len(IntegrationEvent))]
