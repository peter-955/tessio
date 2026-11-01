import asyncio
import uuid

from httpx import AsyncClient

from app.modules.live_events.router import stream_events
from app.shared.events import LiveEvent, LiveEventType
from tests.api.live_events.live_events_test_container import LiveEventsTestContainer
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import sign_up

FRAME_TIMEOUT_SECONDS = 5


async def test_stream_sends_ready_then_live_events(
    client: AsyncClient, container: LiveEventsTestContainer, recording_mailer: RecordingMailer
) -> None:
    await sign_up(client, container, recording_mailer)
    authenticated = await container.authenticate_session.execute(client.cookies["tessio_session"])
    run_id = str(uuid.uuid4())
    frames = stream_events(authenticated, container.stream_live_events)

    try:
        ready_frame = await asyncio.wait_for(anext(frames), FRAME_TIMEOUT_SECONDS)
        await asyncio.wait_for(
            container.live_event_publisher.publish(
                LiveEvent(type=LiveEventType.RUN_CASE_RECORDED, user_id=authenticated.user.id, ids={"runId": run_id})
            ),
            FRAME_TIMEOUT_SECONDS,
        )
        event_frame = await asyncio.wait_for(anext(frames), FRAME_TIMEOUT_SECONDS)
    finally:
        await frames.aclose()

    assert ready_frame.event == "ready"
    assert ready_frame.data == {"userId": str(authenticated.user.id)}
    assert event_frame.event == "run.case_recorded"
    assert event_frame.data == {"projectId": None, "userId": str(authenticated.user.id), "ids": {"runId": run_id}}
