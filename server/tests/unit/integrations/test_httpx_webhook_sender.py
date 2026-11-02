import httpx

from app.modules.integrations.infrastructure import HttpxWebhookSender


def build_sender(status_code: int, sent: list[httpx.Request]) -> HttpxWebhookSender:
    def answer(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(status_code, text="nope" if status_code >= 400 else "ok")

    return HttpxWebhookSender(httpx.AsyncClient(transport=httpx.MockTransport(answer)))


async def test_a_2xx_answer_is_a_success_and_the_body_and_headers_are_sent() -> None:
    sent: list[httpx.Request] = []

    result = await build_sender(204, sent).send("https://8.8.8.8/hook", b'{"a":1}', {"X-Tessio-Event": "run.started"})

    assert (result.is_success, result.response_status, result.error) == (True, 204, None)
    assert sent[0].content == b'{"a":1}'
    assert sent[0].headers["X-Tessio-Event"] == "run.started"


async def test_an_error_answer_keeps_the_status_and_an_excerpt() -> None:
    result = await build_sender(503, []).send("https://8.8.8.8/hook", b"{}", {})

    assert (result.is_success, result.response_status) == (False, 503)
    assert result.error == "The receiver answered HTTP 503. nope"


async def test_a_host_that_resolves_to_a_private_address_is_never_called() -> None:
    sent: list[httpx.Request] = []

    result = await build_sender(200, sent).send("https://127.0.0.1/hook", b"{}", {})

    assert sent == []
    assert result.is_success is False
    assert result.error == "The webhook host resolves to a private, loopback or link-local address."
