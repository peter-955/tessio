import contextlib
import logging
from collections.abc import Callable, Iterator

import httpx
import pytest

from app.modules.integrations.errors import ChatWebhookRejectedError
from app.modules.integrations.infrastructure import HttpxChatWebhookSender
from app.shared.logging import configure_logging

WEBHOOK_URL = "https://hooks.slack.com/services/T0001/B0002/SeCrEt1234"


class RecordingLogHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.NOTSET)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.fixture
def production_log_records() -> Iterator[list[logging.LogRecord]]:
    root_logger = logging.getLogger()
    handlers = list(root_logger.handlers)
    level = root_logger.level
    http_client_levels = {name: logging.getLogger(name).level for name in ("httpx", "httpcore")}
    configure_logging("INFO", None, "test")
    recording_handler = RecordingLogHandler()
    root_logger.addHandler(recording_handler)
    yield recording_handler.records
    root_logger.handlers.clear()
    root_logger.handlers.extend(handlers)
    root_logger.setLevel(level)
    for name, http_client_level in http_client_levels.items():
        logging.getLogger(name).setLevel(http_client_level)


def build_sender(handle: Callable[[httpx.Request], httpx.Response]) -> HttpxChatWebhookSender:
    return HttpxChatWebhookSender(httpx.AsyncClient(transport=httpx.MockTransport(handle)))


@pytest.mark.parametrize("status_code", [200, 202, 204])
async def test_a_success_status_is_a_delivery(status_code: int) -> None:
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status_code, text="ok")

    await build_sender(handle).send(WEBHOOK_URL, {"text": "Hello"})

    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert str(requests[0].url) == WEBHOOK_URL
    assert requests[0].headers["content-type"] == "application/json"
    assert requests[0].content == b'{"text":"Hello"}'


@pytest.mark.parametrize(
    ("status_code", "is_retryable"), [(429, True), (500, True), (503, True), (400, False), (404, False), (410, False)]
)
async def test_an_error_status_says_whether_to_try_again(status_code: int, is_retryable: bool) -> None:
    sender = build_sender(lambda request: httpx.Response(status_code, text="no_service"))

    with pytest.raises(ChatWebhookRejectedError) as error:
        await sender.send(WEBHOOK_URL, {"text": "Hello"})

    assert error.value.is_retryable is is_retryable
    assert error.value.reason == f"Slack or Teams answered HTTP {status_code}."


async def test_a_redirect_is_not_followed() -> None:
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(302, headers={"location": "https://169.254.169.254/latest"})

    with pytest.raises(ChatWebhookRejectedError) as error:
        await build_sender(handle).send(WEBHOOK_URL, {"text": "Hello"})

    assert len(requests) == 1
    assert error.value.is_retryable is False


@pytest.mark.parametrize(
    ("raised", "reason"),
    [
        (httpx.ConnectTimeout("timed out"), "Slack or Teams did not answer in time."),
        (httpx.ConnectError("refused"), "Slack or Teams could not be reached."),
    ],
)
async def test_a_network_error_is_retried_and_never_shows_the_url(raised: httpx.HTTPError, reason: str) -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        raise raised

    with pytest.raises(ChatWebhookRejectedError) as error:
        await build_sender(handle).send(WEBHOOK_URL, {"text": "Hello"})

    assert error.value.is_retryable is True
    assert error.value.reason == reason
    assert "SeCrEt" not in str(error.value)


@pytest.mark.parametrize("status_code", [200, 500])
async def test_a_delivery_never_writes_the_url_to_the_logs(
    production_log_records: list[logging.LogRecord], status_code: int
) -> None:
    sender = build_sender(lambda request: httpx.Response(status_code, text="ok"))

    with contextlib.suppress(ChatWebhookRejectedError):
        await sender.send(WEBHOOK_URL, {"text": "Hello"})

    logged_text = " ".join(f"{record.getMessage()} {record.args}" for record in production_log_records)
    assert "SeCrEt1234" not in logged_text
    assert "hooks.slack.com/services" not in logged_text
