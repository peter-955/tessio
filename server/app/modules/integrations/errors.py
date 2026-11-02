from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class ChatChannelNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Chat channel not found.")


class ChatChannelNameAlreadyUsedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "A chat channel with this name already exists.")


class ChatChannelLimitReachedError(TessioError):
    def __init__(self, limit: int) -> None:
        super().__init__(ErrorCode.CONFLICT, f"A project can have up to {limit} chat channels.")


class ChatWebhookUrlInvalidError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.WEBHOOK_URL_INVALID,
            "Use an https webhook URL on a public host, as Slack or Teams gives it.",
        )


class ChatDeliveryFailedError(TessioError):
    def __init__(self, reason: str) -> None:
        super().__init__(ErrorCode.CHAT_DELIVERY_FAILED, f"The test message was not delivered: {reason}")


class ChatWebhookRejectedError(Exception):
    def __init__(self, reason: str, is_retryable: bool) -> None:
        super().__init__(reason)
        self.reason = reason
        self.is_retryable = is_retryable


class WebhookNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Webhook not found.")


class WebhookDeliveryNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Webhook delivery not found.")


class WebhookLimitReachedError(TessioError):
    def __init__(self, limit: int) -> None:
        super().__init__(ErrorCode.CONFLICT, f"A project can have up to {limit} webhooks.")


class WebhookUrlInvalidError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.WEBHOOK_URL_INVALID,
            "Use an https URL on a public host. Private, loopback and link-local addresses are not allowed.",
        )


class WebhookAttemptFailedError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason
