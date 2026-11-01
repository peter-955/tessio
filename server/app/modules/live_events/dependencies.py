from fastapi import Request, Response

from app.modules.live_events.usecases.stream_live_events import StreamLiveEventsUseCase


def forbid_stream_transformation(response: Response) -> None:
    response.headers["Cache-Control"] = "no-transform"


def get_stream_live_events(request: Request) -> StreamLiveEventsUseCase:
    use_case: StreamLiveEventsUseCase = request.app.state.container.stream_live_events
    return use_case
