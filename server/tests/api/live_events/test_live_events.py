from fastapi.routing import APIRoute
from httpx import AsyncClient

from app.modules.live_events import live_events_router
from app.modules.live_events.dependencies import forbid_stream_transformation


async def test_event_stream_requires_sign_in(client: AsyncClient) -> None:
    response = await client.get("/api/events")

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_SIGNED_IN"


def test_event_stream_forbids_proxy_compression() -> None:
    event_route = next(
        route for route in live_events_router.routes if isinstance(route, APIRoute) and route.path == "/api/events"
    )

    assert forbid_stream_transformation in [dependency.dependency for dependency in event_route.dependencies]
