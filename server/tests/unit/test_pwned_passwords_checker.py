from collections.abc import Callable

import httpx

from app.modules.auth.infrastructure import PwnedPasswordsChecker

PASSWORD_HASH_SUFFIX = "1E4C9B93F3F0682250B6CF8331B7EE68FD8"


def build_checker(handle: Callable[[httpx.Request], httpx.Response]) -> PwnedPasswordsChecker:
    return PwnedPasswordsChecker(httpx.AsyncClient(transport=httpx.MockTransport(handle)))


async def test_password_found_in_the_range_is_breached() -> None:
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, text=f"0018A45C4D1DEF81644B54AB7F969B88D65:1\r\n{PASSWORD_HASH_SUFFIX}:52256179")

    is_breached = await build_checker(handle).is_breached("password")

    assert is_breached is True
    assert str(requests[0].url).endswith("/range/5BAA6")
    assert requests[0].headers["add-padding"] == "true"


async def test_padding_line_with_zero_count_is_not_a_breach() -> None:
    is_breached = await build_checker(lambda _: httpx.Response(200, text=f"{PASSWORD_HASH_SUFFIX}:0")).is_breached(
        "password"
    )

    assert is_breached is False


async def test_password_missing_from_the_range_is_not_breached() -> None:
    is_breached = await build_checker(
        lambda _: httpx.Response(200, text="0018A45C4D1DEF81644B54AB7F969B88D65:1")
    ).is_breached("password")

    assert is_breached is False


async def test_check_is_skipped_when_the_service_fails() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("unreachable", request=request)

    assert await build_checker(handle).is_breached("password") is False
    assert await build_checker(lambda _: httpx.Response(503)).is_breached("password") is False
