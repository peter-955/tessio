from httpx import AsyncClient

SIGN_IN_BODY = {"email": "nobody@tessio.test", "password": "not the right password"}


async def test_write_from_another_site_is_refused(client: AsyncClient) -> None:
    response = await client.post("/api/auth/sign-in", json=SIGN_IN_BODY, headers={"origin": "https://evil.test"})

    assert response.status_code == 403
    assert response.json()["code"] == "ORIGIN_NOT_ALLOWED"


async def test_write_from_the_client_origin_is_allowed(client: AsyncClient) -> None:
    response = await client.post("/api/auth/sign-in", json=SIGN_IN_BODY, headers={"origin": "https://tessio.test"})

    assert response.json()["code"] == "INVALID_CREDENTIALS"


async def test_cross_site_write_without_origin_is_refused(client: AsyncClient) -> None:
    response = await client.post("/api/auth/sign-in", json=SIGN_IN_BODY, headers={"sec-fetch-site": "cross-site"})

    assert response.status_code == 403


async def test_write_from_a_tool_without_browser_headers_is_allowed(client: AsyncClient) -> None:
    response = await client.post("/api/auth/sign-in", json=SIGN_IN_BODY)

    assert response.json()["code"] == "INVALID_CREDENTIALS"


async def test_reads_are_not_checked(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me", headers={"origin": "https://evil.test"})

    assert response.json()["code"] == "NOT_SIGNED_IN"
