from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.modules.auth import AuthenticatedSession, get_signed_in_session
from app.modules.live_events.dependencies import forbid_stream_transformation, get_stream_live_events
from app.modules.live_events.models.ready_event import ReadyEvent
from app.modules.live_events.usecases.stream_live_events import StreamLiveEventsUseCase
from app.modules.users import build_actor

live_events_router = APIRouter(prefix="/api", tags=["live events"])


@live_events_router.get(
    "/events", response_class=EventSourceResponse, dependencies=[Depends(forbid_stream_transformation)]
)
async def stream_events(
    authenticated: Annotated[AuthenticatedSession, Depends(get_signed_in_session)],
    use_case: Annotated[StreamLiveEventsUseCase, Depends(get_stream_live_events)],
) -> AsyncGenerator[ServerSentEvent]:
    async with use_case.open_stream(build_actor(authenticated.user)) as stream:
        yield ServerSentEvent(
            event="ready", data=ReadyEvent(user_id=authenticated.user.id).model_dump(by_alias=True, mode="json")
        )
        async for event in stream:
            yield ServerSentEvent(
                event=event.type.value, data=event.model_dump(by_alias=True, mode="json", exclude={"type"})
            )
